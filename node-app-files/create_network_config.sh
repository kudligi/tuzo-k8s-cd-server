ORG1_KEY=$(ls "/home/gangsta/Desktop/k8s/k8-py-client/node-app-files/channel/crypto-config/peerOrganizations/org1.organizations/users/Admin@org1.organizations/msp/keystore")

ORG2_KEY=$(ls "/home/gangsta/Desktop/k8s/k8-py-client/node-app-files/channel/crypto-config/peerOrganizations/org2.organizations/users/Admin@org2.organizations/msp/keystore")

echo $ORG1_KEY
echo $ORG2_KEY

rm network-config.yaml
cp network-config-template.yaml network-config.yaml

sed -i "s/ORG1_KEY/$ORG1_KEY/g" network-config.yaml
sed -i "s/ORG2_KEY/$ORG2_KEY/g" network-config.yaml