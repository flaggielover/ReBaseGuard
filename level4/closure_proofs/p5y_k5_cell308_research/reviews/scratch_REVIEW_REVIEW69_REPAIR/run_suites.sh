S=/tmp/claude-0/-home-user-ReBaseGuard/000d3115-48ec-594a-b3d0-49b4980206d0/scratchpad/review70
cd $S/tree_9f223c91/level4/closure_proofs/p5y_k5_cell308_research/streams/CLOUD_R1_LINUX_DEV
for v in 3.11 3.12 3.13; do HOME=$S/home GNUPGHOME=$S/home/.gnupg TMPDIR=$S/tmp python$v -B -W error::ResourceWarning -m unittest discover -s tests -v > $S/suites/suite_python$v.txt 2>&1; echo "$v rc=$?" >> $S/suites/rc.txt; done
