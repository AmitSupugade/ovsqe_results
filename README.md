# ovsqe_results
api to import OVSQE test results to google sheets

#How to use
TO_DO

#Example
TO_DO

#Setup script
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
