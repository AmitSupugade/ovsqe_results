# ovsqe_results
api to import OVSQE test results to google sheets
GoogleSheets.py script does basic operations on google sheets such as create, delete, add data etc.

## Examples
#### To upload OVS OFFLOAD results
```
result=()
results+=(64 1 164888 22.90 18.80 24.20 164999 33.90 28.80 344.20)
python OffloadResult.py --result "Test Result upload" --ovs "openvswitch-2.9.0-56.el7fdp.x86_64" --topo "1pf2vf" --data "${results[@]}"
```

## Setup script
```
cat <<'EOT' >> /etc/yum.repos.d/python34.repo
[centos-sclo-rh]
name=CentOS-7 - SCLo rh
baseurl=http://mirror.centos.org/centos/7/sclo/$basearch/rh/
gpgcheck=0
enabled=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-SIG-SCLo
EOT

yum -y install $(echo "
rh-python34
rh-python34-python-tkinter
" | grep -v ^#)

yum -y install scl-utils
scl enable rh-python34 bash

pip install --upgrade google-api-python-client oauth2client
```
