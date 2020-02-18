#!/bin/bash
#
# Copyright IBM Corp. All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0
#

jq --version > /dev/null 2>&1
if [ $? -ne 0 ]; then
	echo "Please Install 'jq' https://stedolan.github.io/jq/ to execute this script"
	echo
	exit 1
fi

starttime=$(date +%s)

echo "POST request Enroll on Org1  ..."
echo
ORG1_TOKEN=$(curl -s -X POST \
  http://35.197.138.142:4000/users \
  -H "content-type: application/x-www-form-urlencoded" \
  -d 'username=uday&orgName=Org1')
echo $ORG1_TOKEN
ORG1_TOKEN=$(echo $ORG1_TOKEN | jq ".token" | sed "s/\"//g")
echo

# echo "POST invoke chaincode on peers of Org1 and Org2"
# echo
# TRX_ID=$(curl -s -X POST \
#   http://35.197.138.142:4000/channels/common/chaincodes/very-simple \
#   -H "authorization: Bearer $ORG1_TOKEN" \
#   -H "content-type: application/json" \
#   -d '{
# 	"peers": ["peer0.org1.organizations"],
# 	"fcn":"ping",
# 	"args":[""]
# }')
# echo "Transaction ID is $TRX_ID"
# echo
# echo

# echo "GET query Channels"
# echo
# curl -s -X GET \
#   "http://35.197.138.142:4000/channels?peer=peer0.org.redeem.merchant.one" \
#   -H "authorization: Bearer $ORG1_TOKEN" \
#   -H "content-type: application/json"
# echo
# echo


# echo "GET query Installed chaincodes"
# echo
# curl -s -X GET \
#   "http://35.197.138.142:4000/chaincodes?peer=peer0.org.redeem.merchant.one" \
#   -H "authorization: Bearer $ORG1_TOKEN" \
#   -H "content-type: application/json"
# echo
# echo

# echo "GET query Instantiated chaincodes"
# echo
# curl -s -X GET \
#   "http://35.197.138.142:4000/chaincodes?peer=peer0.org.issue.merchant.two" \
#   -H "authorization: Bearer $ORG1_TOKEN" \
#   -H "content-type: application/json"
# echo
# echo




# echo "POST invoke chaincode on peers of Org1 with org1 token"
# echo
# VALUES=$(curl -s -X POST \
#   http://35.197.138.142:4000/channels/common/chaincodes/very-simple \
#   -H "authorization: Bearer $ORG1_TOKEN" \
#   -H "content-type: application/json" \
#   -d "{
#   \"peers\": [\"peer0.org.redeem.merchant.one\"],
#   \"fcn\":\"ping\",
#   \"args\":[\"\"]
# }")
# echo $VALUES

# echo "POST invoke chaincode on peers of Org1 with org1 token"
# echo
# VALUES=$(curl -s -X POST \
#   http://35.197.138.142:4000/channels/common/chaincodes/tuzo-cc \
#   -H "authorization: Bearer $ORG1_TOKEN" \
#   -H "content-type: application/json" \
#   -d "{
#   \"peers\": [\"peer0.org.redeem.merchant.one\"],
#   \"fcn\":\"ping\",
#   \"args\":[\"\"]
# }")
# echo $VALUES

# echo "POST invoke chaincode on peers of Org2 with org1 token"
# echo
# VALUES=$(curl -s -X POST \
#   http://35.197.138.142:4000/channels/common/chaincodes/tuzo-cc \
#   -H "authorization: Bearer $ORG1_TOKEN" \
#   -H "content-type: application/json" \
#   -d "{
#   \"peers\": [\"peer0.org.issue.merchant.two\"],
#   \"fcn\":\"ping\",
#   \"args\":[\"\"]
# }")
# echo $VALUES

# echo "POST invoke chaincode on peers of Org1 and Org2"
# echo
# VALUES=$(curl -s -X POST \
#   http://35.197.138.142:4000/channels/common/chaincodes/tuzo-cc \
#   -H "authorization: Bearer $ORG1_TOKEN" \
#   -H "content-type: application/json" \
#   -d "{
#   \"peers\": [\"peer0.org1.organizations\"],
#   \"fcn\":\"invoke\",
#   \"args\":[\"a\",\"b\",\"3\"]
# }")
# echo $VALUES

# echo "POST invoke chaincode on peers of Org1 and Org2"
# echo
# VALUES=$(curl -s -X POST \
#   http://35.197.138.142:4000/channels/common/chaincodes/tuzo-cc \
#   -H "authorization: Bearer $ORG1_TOKEN" \
#   -H "content-type: application/json" \
#   -d "{
#   \"peers\": [\"peer0.org1.organizations\"],
#   \"fcn\":\"query\",
#   \"args\":[\"a\"]
# }")
# echo $VALUES



