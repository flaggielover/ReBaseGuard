/* DEV_FIXED_IDLE_ONLY proposal. No producer/model/green fallback exists here.
 * Included by manager_authority.c; only its prepared opaque authority is used.
 */
static int decimal_zero(const char *s, uint64_t *v) {
  if (!strcmp(s, "0")) {
    *v = 0;
    return 1;
  }
  return positive_decimal(s, v);
}
static const char *const safety_keys[] = {"protocol",
                                          "scope",
                                          "collector",
                                          "G",
                                          "host_epoch_seq",
                                          "host_boot",
                                          "guest_boot",
                                          "package",
                                          "guest",
                                          "runtime",
                                          "policy",
                                          "sequence",
                                          "nonce",
                                          "previous_sha256",
                                          "qpc_frequency",
                                          "interval_start_qpc",
                                          "interval_end_qpc",
                                          "signed_qpc",
                                          "event_loss",
                                          "unknown_ticks",
                                          "coverage_complete",
                                          "quiet",
                                          "policy_stable",
                                          "suspend_epoch",
                                          "source_instance",
                                          "vm_lifetime_sha256",
                                          "source_evidence_sha256"};
int p309_authority_safety_current(const struct p309_start_authority *a) {
  if (!a || !a->control || p309_authority_stopped(a))
    return 0;
  if (!p309_peer_alive(a->safety.monitor) || !p309_peer_alive(a->host.relay) ||
      !p309_lease_current(&a->control->lease, clock_ns())) {
    p309_authority_stop(a);
    return 0;
  }
  return !p309_authority_stopped(a);
}
int p309_authority_safety_watchdog(const struct p309_start_authority *a) {
  if (!a || !a->control || p309_authority_stopped(a))
    return 0;
  if (!p309_peer_alive(a->safety.monitor) ||
      (atomic_load(&a->host.relay_published) &&
       !p309_peer_alive(a->host.relay)) ||
      !p309_lease_watchdog(&a->control->lease, clock_ns())) {
    p309_authority_stop(a);
    return 0;
  }
  return !p309_authority_stopped(a);
}
int p309_authority_safety_poll(struct p309_start_authority *a) {
  if (!a || getpid() != (pid_t)a->r.broker_pid || !a->host.reserved ||
      p309_authority_stopped(a))
    return 0;
  if (atomic_exchange(&a->safety.polling, 1)) {
    p309_authority_stop(a);
    return 0;
  }
  int ok = 0;
  char observer_pin[65], ack_pin[65];
  int64_t issued = clock_ns();
  long long previous_deadline = p309_lease_begin(&a->control->lease, issued);
  if (previous_deadline == P309_LEASE_INVALID || issued < 0 ||
      issued > INT64_MAX - 2000000000LL ||
      !p309_peer_alive(a->safety.monitor) || a->safety.sequence > 4096 ||
      !digest_named("host-observer-v9.spki.sha256", observer_pin) ||
      !digest_named("host-anchor-ack-v10.spki.sha256", ack_pin) ||
      !strcmp(observer_pin, ack_pin))
    goto done;
  unsigned char random[32];
  char nonce[65];
  if (getrandom(random, sizeof random, 0) != (ssize_t)sizeof random)
    goto done;
  for (size_t i = 0; i < 32; i++)
    snprintf(nonce + 2 * i, 3, "%02x", random[i]);
  unsigned char request[2048];
  int q = snprintf(
      (char *)request, sizeof request,
      "protocol=P309_ROLLING_SAFETY_REQUEST/"
      "1\nscope=DEV_FIXED_IDLE_ONLY\nG=%s\nhost_epoch_seq=%s\nhost_boot=%"
      "s\nguest_boot=%s\npackage=%s\nguest=%s\nruntime=%s\npolicy=%s\nsequence="
      "%llu\nnonce=%s\nprevious_sha256=%s\nvm_lifetime_sha256=%s\n",
      a->r.generation, a->host.epoch, a->host.host_boot, a->host.guest_boot,
      a->r.package, a->host.guest, a->host.runtime, a->host.policy,
      (unsigned long long)a->safety.sequence, nonce, a->safety.previous,
      a->host.vm_lifetime);
  unsigned char wire[4480];
  size_t n = 0;
  if (q <= 0 || (size_t)q >= sizeof request ||
      !p309_monitor_exchange(a->control, request, (size_t)q, wire, &n) ||
      n <= 384 || !p309_observer_verify(wire, n - 384, wire + n - 384))
    goto done;
  char v[27][65];
  uint64_t seq, freq, begin, end, signed_at, loss, unknown, suspend;
  if (!canonical_fields(wire, n - 384, safety_keys, 27, v) ||
      strcmp(v[0], "P309_HOST_SAFETY_FACTS/1") ||
      strcmp(v[1], "DEV_FIXED_IDLE_ONLY") ||
      strcmp(v[2], "LIVE_ROLLING_ETW_V1") || strcmp(v[3], a->r.generation) ||
      strcmp(v[4], a->host.epoch) || strcmp(v[5], a->host.host_boot) ||
      strcmp(v[6], a->host.guest_boot) || strcmp(v[7], a->r.package) ||
      strcmp(v[8], a->host.guest) || strcmp(v[9], a->host.runtime) ||
      strcmp(v[10], a->host.policy) || !positive_decimal(v[11], &seq) ||
      seq != a->safety.sequence || strcmp(v[12], nonce) ||
      strcmp(v[13], a->safety.previous) || !positive_decimal(v[14], &freq) ||
      freq > 1000000000 || !decimal_zero(v[15], &begin) ||
      !positive_decimal(v[16], &end) || !positive_decimal(v[17], &signed_at) ||
      !decimal_zero(v[18], &loss) || loss || !decimal_zero(v[19], &unknown) ||
      unknown || strcmp(v[20], "1") || strcmp(v[21], "1") ||
      strcmp(v[22], "1") || !decimal_zero(v[23], &suspend) ||
      !lowerhex(v[24], 32) || strcmp(v[25], a->host.vm_lifetime) ||
      !lowerhex(v[26], 64))
    goto done;
  if (end < begin || end - begin < 60 * freq || end - begin > 105 * freq ||
      signed_at < end || signed_at - end > freq / 2)
    goto done;
  if (a->safety.sequence > 1 &&
      (freq != a->safety.frequency || signed_at <= a->safety.last_signed ||
       end <= a->safety.last_end ||
       (begin > a->safety.last_end && begin - a->safety.last_end > 45 * freq) ||
       suspend != a->safety.suspend_epoch || strcmp(v[24], a->safety.source)))
    goto done;
  int64_t completed = clock_ns();
  if (completed < issued || completed - issued > 1000000000LL ||
      !p309_peer_alive(a->safety.monitor) || p309_authority_stopped(a))
    goto done;
  /* Every success requires a new signed frame and nonce. No refresh of an old
   * lease while a request is pending. Host QPC and guest BOOTTIME never share
   * a numeric axis; signed age and measured RTT are separately bounded. */
  if (!sha_hex(wire, n, a->safety.previous))
    goto done;
  a->safety.frequency = freq;
  a->safety.last_signed = signed_at;
  a->safety.last_end = end;
  a->safety.suspend_epoch = suspend;
  strcpy(a->safety.source, v[24]);
  a->safety.sequence++;
  if (p309_authority_stopped(a) ||
      !p309_lease_publish(&a->control->lease, previous_deadline, issued,
                          clock_ns()) ||
      p309_authority_stopped(a))
    goto done;
  ok = 1;
done:
  if (!ok) {
    p309_authority_stop(a);
  }
  atomic_store(&a->safety.polling, 0);
  return ok;
}
