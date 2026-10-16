/* Included ONLY by manager_authority.c: no caller-built proof/signing API. */
static int digest_named(const char *name, char out[65]) {
  int d = directory(PACKAGE_DIR);
  if (d < 0)
    return 0;
  char raw[65];
  int ok = !read_fixed(d, name, raw, sizeof raw, 0444);
  close(d);
  if (!ok || raw[64] != '\n')
    return 0;
  memcpy(out, raw, 64);
  out[64] = 0;
  return hex64(out);
}
static int lowerhex(const char *s, size_t n) {
  if (strlen(s) != n)
    return 0;
  for (size_t i = 0; i < n; i++)
    if (!((s[i] >= '0' && s[i] <= '9') || (s[i] >= 'a' && s[i] <= 'f')))
      return 0;
  return 1;
}
static int positive_decimal(const char *s, uint64_t *v) {
  if (!s || s[0] < '1' || s[0] > '9')
    return 0;
  uint64_t x = 0;
  for (size_t i = 0; s[i]; i++) {
    if (s[i] < '0' || s[i] > '9' ||
        x > ((uint64_t)INT64_MAX - (unsigned)(s[i] - '0')) / 10)
      return 0;
    x = x * 10 + (unsigned)(s[i] - '0');
  }
  *v = x;
  return 1;
}
static int canonical_fields(const unsigned char *wire, size_t len,
                            const char *const *keys, size_t count,
                            char values[][65]) {
  size_t at = 0;
  for (size_t i = 0; i < count; i++) {
    size_t k = strlen(keys[i]);
    if (at + k + 2 > len || memcmp(wire + at, keys[i], k) ||
        wire[at + k] != '=')
      return 0;
    at += k + 1;
    size_t n = 0;
    while (at < len && wire[at] != '\n') {
      unsigned char ch = wire[at++];
      if (ch < 33 || ch > 126 || ch == '=' || n >= 64)
        return 0;
      values[i][n++] = (char)ch;
    }
    if (at >= len || !n)
      return 0;
    values[i][n] = 0;
    at++;
  }
  return at == len;
}
static int signed_fields(const unsigned char *wire, size_t bytes,
                         const char *const *keys, size_t count,
                         char values[][65]) {
  return bytes > 384 && bytes <= 4480 &&
         p309_anchor_verify(wire, bytes - 384, wire + bytes - 384) &&
         canonical_fields(wire, bytes - 384, keys, count, values);
}
static int durable_signed(const char *name, const unsigned char *bytes,
                          size_t n) {
  int d = directory(STATE_DIR);
  if (d < 0)
    return 0;
  int f = openat(d, name, O_WRONLY | O_CREAT | O_EXCL | O_NOFOLLOW | O_CLOEXEC,
                 0600);
  if (f < 0) {
    close(d);
    return 0;
  }
  int ok = !write_all(f, bytes, n) && !fsync(f);
  if (close(f))
    ok = 0;
  if (fsync(d))
    ok = 0;
  close(d);
  return ok;
}
static int sha_hex(const unsigned char *raw, size_t n, char out[65]) {
  unsigned char digest[32];
  unsigned int len = 0;
  if (!EVP_Digest(raw, n, digest, &len, EVP_sha256(), NULL) || len != 32)
    return 0;
  for (size_t i = 0; i < 32; i++)
    snprintf(out + 2 * i, 3, "%02x", digest[i]);
  return 1;
}
static int no_password(char *buf, int size, int rw, void *user) {
  (void)buf;
  (void)size;
  (void)rw;
  (void)user;
  return 0;
}
/* Private helper, deliberately NOT an exported generic signing API. Its only
 * callers below construct the two fixed purpose objects from opaque authority.
 * Never creates a key and never accepts a caller-selected key/path/provider. */
static int sign_internal_proof(const unsigned char *body, size_t n,
                               unsigned char signature[384]) {
  if (geteuid() != 0 || !body || !n || n > 4096)
    return 0;
  int d = directory(PACKAGE_DIR);
  if (d < 0)
    return 0;
  int f = openat(d, "guest-blocked-v10.private.pem",
                 O_RDONLY | O_CLOEXEC | O_NOFOLLOW);
  close(d);
  if (f < 0)
    return 0;
  unsigned char pem[8192];
  struct stat st;
  int ok = 0;
  size_t at = 0;
  BIO *bio = NULL;
  EVP_PKEY *key = NULL;
  EVP_MD_CTX *ctx = NULL;
  EVP_PKEY_CTX *pk = NULL;
  if (fstat(f, &st) || !S_ISREG(st.st_mode) || st.st_uid ||
      (st.st_mode & 0777) != 0400 || st.st_nlink != 1 || st.st_size <= 0 ||
      st.st_size > (off_t)sizeof pem)
    goto done;
  while (at < (size_t)st.st_size) {
    ssize_t got = read(f, pem + at, (size_t)st.st_size - at);
    if (got <= 0)
      goto done;
    at += (size_t)got;
  }
  bio = BIO_new_mem_buf(pem, (int)at);
  if (!bio)
    goto done;
  key = PEM_read_bio_PrivateKey(bio, NULL, no_password, NULL);
  if (!key || !EVP_PKEY_is_a(key, "RSA") || EVP_PKEY_get_bits(key) != 3072 ||
      EVP_PKEY_get_size(key) != 384)
    goto done;
  unsigned char *der = NULL;
  int dn = i2d_PUBKEY(key, &der);
  char actual[65], expected[65];
  int pin_ok = dn > 0 && der && sha_hex(der, (size_t)dn, actual) &&
               digest_named("guest-blocked-v10.spki.sha256", expected) &&
               !strcmp(actual, expected);
  OPENSSL_free(der);
  if (!pin_ok)
    goto done;
  ctx = EVP_MD_CTX_new();
  size_t sn = 384;
  if (!ctx || EVP_DigestSignInit(ctx, &pk, EVP_sha256(), NULL, key) <= 0 ||
      EVP_PKEY_CTX_set_rsa_padding(pk, RSA_PKCS1_PADDING) <= 0)
    goto done;
  ok = EVP_DigestSign(ctx, signature, &sn, body, n) > 0 && sn == 384;
done:
  close(f);
  EVP_MD_CTX_free(ctx);
  EVP_PKEY_free(key);
  BIO_free(bio);
  OPENSSL_cleanse(pem, sizeof pem);
  return ok;
}
static const char *const context_keys[] = {"protocol",
                                           "scope",
                                           "G",
                                           "host_epoch_seq",
                                           "host_boot",
                                           "guest_boot",
                                           "package",
                                           "guest",
                                           "runtime",
                                           "policy",
                                           "challenge",
                                           "host_record_seq",
                                           "host_record_sha256",
                                           "anchor_binding_sha256",
                                           "checkpoint",
                                           "vm_lifetime_sha256",
                                           "guest_root_public_spki_sha256",
                                           "ack_public_spki_sha256"};
static const char *const reserve_keys[] = {"protocol",
                                           "scope",
                                           "G",
                                           "host_epoch_seq",
                                           "host_boot",
                                           "guest_boot",
                                           "package",
                                           "guest",
                                           "runtime",
                                           "policy",
                                           "challenge",
                                           "host_record_seq",
                                           "host_record_sha256",
                                           "anchor_binding_sha256",
                                           "checkpoint"};
static const char *const final_keys[] = {"protocol",
                                         "scope",
                                         "G",
                                         "host_epoch_seq",
                                         "host_boot",
                                         "guest_boot",
                                         "package",
                                         "guest",
                                         "runtime",
                                         "policy",
                                         "workerInv",
                                         "brokerInv",
                                         "challenge",
                                         "blocked_proof_sha256",
                                         "host_record_seq",
                                         "host_record_sha256",
                                         "anchor_binding_sha256",
                                         "checkpoint"};
static int context_accept(struct p309_start_authority *a,
                          const unsigned char *wire, size_t n) {
  char v[18][65], guest_pin[65], host_pin[65];
  uint64_t epoch, seq;
  if (!signed_fields(wire, n, context_keys, 18, v) ||
      strcmp(v[0], "P309_HOST_VM_SESSION/1") ||
      strcmp(v[1], "DEV_FIXED_IDLE_ONLY") || strcmp(v[2], a->r.generation) ||
      !positive_decimal(v[3], &epoch) || !lowerhex(v[4], 32) ||
      strcmp(v[5], a->host.guest_boot) || strcmp(v[6], a->r.package) ||
      strcmp(v[7], a->host.guest) || strcmp(v[8], a->host.runtime) ||
      strcmp(v[9], a->host.policy) || strcmp(v[10], a->host.challenge) ||
      !positive_decimal(v[11], &seq))
    return 0;
  for (size_t i = 12; i < 18; i++)
    if (!lowerhex(v[i], 64))
      return 0;
  if (!digest_named("guest-blocked-v10.spki.sha256", guest_pin) ||
      !digest_named("host-anchor-ack-v10.spki.sha256", host_pin) ||
      strcmp(v[16], guest_pin) || strcmp(v[17], host_pin))
    return 0;
  /* Expected session fields come from this distinct purpose-signed descriptor,
   * never from the ACK being validated. Host factory, enrollment and VM
   * lifetime remain required trusted sources; a signature is not hardware
   * attestation. O_EXCL means no replay/overwrite/resume within this state. */
  if (!durable_signed("host-session-v10.signed", wire, n))
    return 0;
  strcpy(a->host.epoch, v[3]);
  strcpy(a->host.host_boot, v[4]);
  strcpy(a->host.anchor, v[13]);
  strcpy(a->host.checkpoint, v[14]);
  a->host.reserve_seq = seq;
  strcpy(a->host.reserve_record, v[12]);
  strcpy(a->host.vm_lifetime, v[15]);
  strcpy(a->host.guest_pin, v[16]);
  return 1;
}
static int common_ack(const struct p309_start_authority *a, char v[][65]) {
  return !strcmp(v[1], "DEV_FIXED_IDLE_ONLY") &&
         !strcmp(v[2], a->r.generation) && !strcmp(v[3], a->host.epoch) &&
         !strcmp(v[4], a->host.host_boot) &&
         !strcmp(v[5], a->host.guest_boot) && !strcmp(v[6], a->r.package) &&
         !strcmp(v[7], a->host.guest) && !strcmp(v[8], a->host.runtime) &&
         !strcmp(v[9], a->host.policy);
}
static int host_reserve_once(struct p309_start_authority *a) {
  /* G/challenge generated locally before transport; neither is caller data. */
  if (!digest_named("guest-v9.sha256", a->host.guest) ||
      !digest_named("runtime-v9.sha256", a->host.runtime) ||
      !digest_named("policy-v9.sha256", a->host.policy))
    return 0;
  size_t j = 0;
  for (size_t i = 0; i < 36; i++)
    if (a->r.boot[i] != '-') {
      if (j >= 32)
        return 0;
      a->host.guest_boot[j++] = a->r.boot[i];
    }
  a->host.guest_boot[j] = 0;
  if (!lowerhex(a->host.guest_boot, 32))
    return 0;
  unsigned char random[32];
  if (getrandom(random, sizeof random, 0) != (ssize_t)sizeof random)
    return 0;
  for (size_t i = 0; i < 32; i++)
    snprintf(a->host.challenge + 2 * i, 3, "%02x", random[i]);
  char root_pin[65];
  if (!p309_peer_alive(a->safety.monitor) ||
      !digest_named("guest-blocked-v10.spki.sha256", root_pin))
    return 0;
  struct {
    char generation[33], invocation[33], code_sha256[65];
    uint32_t pid, uid;
    uint64_t start;
  } monitor = {0};
  strcpy(monitor.generation, a->r.generation);
  strcpy(monitor.invocation, a->safety.monitor->invocation);
  strcpy(monitor.code_sha256, a->safety.monitor->code_sha256);
  monitor.pid = (uint32_t)a->safety.monitor->pid;
  monitor.uid = (uint32_t)a->safety.monitor->uid;
  monitor.start = a->safety.monitor->start;
  if (!durable_signed("monitor-v9.claim", (unsigned char *)&monitor,
                      sizeof monitor) ||
      !p309_peer_alive(a->safety.monitor))
    return 0;
  unsigned char req[4480];
  int q = snprintf((char *)req, 4096,
                   "protocol=P309_GUEST_ROOT_PRESTART/"
                   "1\nscope=DEV_FIXED_IDLE_ONLY\nG=%s\nguest_boot=%s\npackage="
                   "%s\nguest=%s\nruntime=%s\npolicy=%s\nchallenge=%"
                   "s\napproval_sha256=%s\nguest_root_public_spki_sha256=%s\n",
                   a->r.generation, a->host.guest_boot, a->r.package,
                   a->host.guest, a->host.runtime, a->host.policy,
                   a->host.challenge, a->r.approval, root_pin);
  if (q <= 0 || q >= 4096 || !sign_internal_proof(req, (size_t)q, req + q) ||
      !durable_signed("host-prestart-v10.claim", req, (size_t)q + 384))
    return 0;
  unsigned char context[4480], ack[4480];
  size_t cn = 0, an = 0;
  if (!p309_host_reserve_exchange(a->control, req, (size_t)q + 384, context,
                                  &cn, ack, &an) ||
      !context_accept(a, context, cn) || p309_authority_stopped(a))
    return 0;
  char v[15][65];
  uint64_t seq;
  if (!signed_fields(ack, an, reserve_keys, 15, v) ||
      strcmp(v[0], "P309_HOST_ANCHOR_RESERVE_ACK/1") || !common_ack(a, v) ||
      strcmp(v[10], a->host.challenge) || !positive_decimal(v[11], &seq) ||
      seq != a->host.reserve_seq || strcmp(v[12], a->host.reserve_record) ||
      strcmp(v[13], a->host.anchor) || strcmp(v[14], a->host.checkpoint) ||
      !durable_signed("host-reserve-v10.consumed", ack, an) ||
      p309_authority_stopped(a))
    return 0;
  a->host.reserved = 1;
  return 1;
}
int p309_authority_note_guardian_ready(
    const struct p309_start_authority *constant, int guardian_fd) {
  if (!constant || getpid() != (pid_t)constant->r.broker_pid ||
      guardian_fd != guardian_record.fd || !guardian_record.bus ||
      !alive(guardian_fd) || !p309_authority_current(constant))
    return 0;
  struct p309_start_authority *a = (struct p309_start_authority *)constant;
  if (atomic_load(&a->host.guardian_ready))
    return 0;
  /* Called only by broker_link immediately after the authenticated READY and
   * actual independent guardian manager/pidfd verification, before publication.
   */
  struct {
    char magic[16], generation[33], invocation[33];
    uint32_t pid;
    uint64_t start;
  } record = {0};
  memcpy(record.magic, "P309_READY_V9", 13);
  strcpy(record.generation, a->r.generation);
  strcpy(record.invocation, guardian_record.inv);
  record.pid = guardian_record.pid;
  record.start = start_ticks((pid_t)record.pid);
  if (!record.start ||
      !durable_signed("guardian-ready-v9.claim", (unsigned char *)&record,
                      sizeof record) ||
      !alive(guardian_fd) || p309_authority_stopped(a))
    return 0;
  strcpy(a->host.guardian_inv, guardian_record.inv);
  atomic_store(&a->host.guardian_ready, 1);
  return 1;
}
int p309_authority_host_ack_consume(
    const struct p309_start_authority *constant) {
  if (!constant || getpid() != (pid_t)constant->r.broker_pid)
    return 0;
  struct p309_start_authority *a = (struct p309_start_authority *)constant;
  if (!a->host.reserved || !atomic_load(&a->host.guardian_ready) ||
      !p309_authority_release_pending(a) ||
      atomic_exchange(&a->host.final_consumed, 1) ||
      !p309_authority_current(a) || !p309_authority_release_pending(a) ||
      !guardian_record.bus || !alive(guardian_record.fd))
    return 0;
  uint32_t guardian_pid;
  char guardian_inv[33];
  if (facts(guardian_record.bus, "rebaseguard-p309-guardian.service",
            &guardian_pid, guardian_inv, 0) ||
      guardian_pid != guardian_record.pid ||
      strcmp(guardian_inv, a->host.guardian_inv) ||
      !p309_authority_release_pending(a))
    return 0;
  unsigned char proof[4480];
  char proof_hash[65];
  int q = snprintf(
      (char *)proof, 4096,
      "protocol=P309_GUEST_BLOCKED_INVOCATION/"
      "1\nscope=DEV_FIXED_IDLE_ONLY\nG=%s\nhost_epoch_seq=%s\nhost_boot=%"
      "s\nguest_boot=%s\npackage=%s\nguest=%s\nruntime=%s\npolicy=%"
      "s\nworkerInv=%s\nbrokerInv=%s\nguardianInv=%s\nchallenge=%s\nreserve_"
      "record_seq=%llu\nreserve_record_sha256=%s\nanchor_binding_sha256=%"
      "s\ncheckpoint=%s\nvm_lifetime_sha256=%s\nguest_root_public_spki_sha256=%"
      "s\n",
      a->r.generation, a->host.epoch, a->host.host_boot, a->host.guest_boot,
      a->r.package, a->host.guest, a->host.runtime, a->host.policy,
      a->r.worker_inv, a->r.broker_inv, a->host.guardian_inv, a->host.challenge,
      (unsigned long long)a->host.reserve_seq, a->host.reserve_record,
      a->host.anchor, a->host.checkpoint, a->host.vm_lifetime,
      a->host.guest_pin);
  if (q <= 0 || q >= 4096 || !sha_hex(proof, (size_t)q, proof_hash) ||
      !sign_internal_proof(proof, (size_t)q, proof + q) ||
      !durable_signed("guest-blocked-v10.claim", proof, (size_t)q + 384) ||
      !p309_authority_release_pending(a))
    return 0;
  unsigned char ack[4480];
  size_t an = 0;
  if (!p309_host_exchange(a->control, proof, (size_t)q + 384, ack, &an) ||
      !p309_authority_release_pending(a))
    return 0;
  char v[18][65];
  uint64_t seq;
  if (!signed_fields(ack, an, final_keys, 18, v) ||
      strcmp(v[0], "P309_HOST_ANCHOR_ACK/1") || !common_ack(a, v) ||
      strcmp(v[10], a->r.worker_inv) || strcmp(v[11], a->r.broker_inv) ||
      strcmp(v[12], a->host.challenge) || strcmp(v[13], proof_hash) ||
      !positive_decimal(v[14], &seq) || seq <= a->host.reserve_seq ||
      !lowerhex(v[15], 64) || strcmp(v[16], a->host.anchor) ||
      strcmp(v[17], a->host.checkpoint) || !p309_authority_release_pending(a))
    return 0;
  /* Durable before dispatch, never clear/retry after lost ACK/crash/STOP.
   * Host anti-rollback relies on its independent durable reserve/consume,
   * never this guest-local file or the existence of active-v9.bin. */
  if (!durable_signed("host-final-v10.consumed", ack, an) ||
      !p309_authority_release_pending(a) || !p309_authority_current(a) ||
      !p309_authority_release_pending(a))
    return 0;
  atomic_store(&a->host.final_consumed, 2);
  return 1;
}
