# ovsqe_results
- API to import OVSQE test results to google sheets

- 'GoogleSheet' class can be used to create, delete, modify, add data to google sheet.

- 'GoogleDrive' class can be used to search spreadsheet in google drive by its name.

- 'OffloadResults' can be used to upload results of ovs offload tests to google sheets. It checks to see if result sheet exists in google drive, if exists, it will update results in that sheet if not, it will create new sheet and update results in that sheet.

- You need to write script similar to OffloadResults.py as per your need to upload test results in Google sheet. Kindly refer [wiki page](https://github.com/AmitSupugade/ovsqe_results/wiki) for guidelines.

# How to use
- Run setup script below

- clone this api repository and cd to the repository

- Download ['client_secret.json'](http://netqe-infra01.knqe.lab.eng.bos.redhat.com/ovs_offload/client_secret.json) and ['token.json'](http://netqe-infra01.knqe.lab.eng.bos.redhat.com/ovs_offload/token.json) files from netqe infra server in bos lab

- Run script to import results

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

## Upload your results
- If you want to use this api to upload your results to Google sheet, you need to write a python script.

- Kindly refer [wiki page](https://github.com/AmitSupugade/ovsqe_results/wiki) for guidelines to write scripts to upload your results
