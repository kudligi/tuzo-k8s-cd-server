const shim = require("fabric-shim");
const logger = shim.newLogger('chaincode');

const Validations = require("./helpers/validations");
const Utils = require("./helpers/utils");

const ClientIdentity = shim.ClientIdentity;


var cc = class {
    
    async Init(stub) {
        console.log("===============Chaincode init===============");
        const ret = stub.getFunctionAndParameters();
        const args = ret.params;

        const ownerMspId = new ClientIdentity(stub).getMSPID();
       
        console.log(`=============== MSP calling init is ${ownerMspId} ===============`);

        const bufferedName =  args[0];
        const bufferedSymbol = args[1];
        const bufferedLeadMerchantMSP = args[2];

        let lead_wallet_body = {}
        lead_wallet_body.balance = 0;
        lead_wallet_body.expired_points = 0;

        try {
            await stub.putState("name", bufferedName);
            await stub.putState("symbol", bufferedSymbol);
            await stub.putState("leadMSP", bufferedLeadMerchantMSP);
            await stub.putState("leadWallet", Utils.jsonToBuffer(lead_wallet_body));
            return shim.success();
        }catch (error) {
            return  shim.error(error);
        }
    } 

    /**
   * @dev Invoke Token Chaincode
   */
  async Invoke(stub) {
    console.log("========= Token chaincode Invoke =========");
    const ret = stub.getFunctionAndParameters();

    const method = this[ret.fcn];
    if (!method) {
      console.error(`No method of name: ${ret.fcn} found`);
      return shim.error();
    }
    console.log(`========= Calling Function ${ret.fcn} =========`);

    try {
      const payload = await method(stub, ret.params, this);
      return shim.success(payload);
    } catch (error) {
      console.error(error);
      return shim.error(error);
    }
  }

  async createCustomerAccount(stub, args) {
        logger.info("================ Create Customer Called ================");
       
        let cid = new ClientIdentity(stub);
        let x509 = cid.getX509Certificate();
        let fingerPrint = x509.fingerPrint;
        let account_id = x509.issuer.organizationName.toString() + "." + x509.subject.commonName.toString();
        let account_key = "customer_account." + account_id;
        let wallet_key = "customer_wallet." + account_id; 

        let payload = {}

        let account_body = {
            name: x509.subject.commonName.toString(),
            Doctype: "Customer_Account",
            fingerprint: fingerPrint
        }


        let wallet_body = {
            belongs_to: account_key,
            Doctype: "Customer_Wallet",
            balance: 0
        }

        // let already_exists_bytes = await stub.getState(account_key);
        // if 
        let A = await stub.getState(account_key);
        if (A.toString().length != 0) {
            throw new Error("Account already exists for caller");
        }


        try {
            await stub.putState(account_key, Utils.jsonToBuffer(account_body));
            await stub.putState(wallet_key, Utils.jsonToBuffer(wallet_body));
        }catch (error) {
            return shim.error(error);
        }

        
        payload.account_key = account_key;
        payload.account_body = account_body;
        payload.wallet_key = wallet_key;
        payload.wallet_body = wallet_body;
        

        return Buffer.from(JSON.stringify(payload), 'utf8');
  }

  async mint(stub, args){
    let cid = new ClientIdentity(stub);

    let callerMSP = cid.getMSPID();
    
    let LeadMSP = await stub.getState("leadMSP");
    LeadMSP = LeadMSP.toString();

    logger.info("caller MSP is ", callerMSP);
    logger.info("lead MSP is ", LeadMSP);

    if (callerMSP != LeadMSP) {
        throw new Error('Caller does not belong to lead Organization')
    }

    let mintAllowed = cid.getAttributeValue("MINT");

    if (mintAllowed == null || mintAllowed != "YES") {
        throw new Error('Caller does not have required authorization to mint new points')
    }

    let mintValue = parseInt(args[0]);

    if (mintValue <= 0) {
        throw new Error("Value to be minted must be > 0");
    }

    let answer = {}
    let leadWallet = await stub.getState("leadWallet");
    leadWallet = JSON.parse(leadWallet.toString());

    logger.info("$$$$$$$$$$$$$ the lead wallet is", leadWallet);
    // answer.oldLeadWallet = leadWallet;
    leadWallet.balance += mintValue;

    try {
        await stub.putState("leadWallet", Utils.jsonToBuffer(leadWallet));
    }catch (error) {
        return shim.error(error);
    }

    answer.callerMSP = callerMSP;
    answer.leadMSP = LeadMSP;
    answer.mint = mintAllowed;
    answer.leadWallet = leadWallet;

    return Buffer.from(JSON.stringify(answer), 'utf8');
  }

  async issue(stub, args) {
    let cid = new ClientIdentity(stub);

    let callerMSP = cid.getMSPID();
    
    let LeadMSP = await stub.getState("leadMSP");
    LeadMSP = LeadMSP.toString();

    logger.info("caller MSP is ", callerMSP);
    logger.info("lead MSP is ", LeadMSP);

    if (callerMSP != LeadMSP) {
        throw new Error('Caller does not belong to lead Organization')
    }

    let issueAllowed = cid.getAttributeValue("ISSUE");

    if (issueAllowed != "YES") {
        throw new Error("Caller does not have authorization to issue points")
    }

    let pointsVal = args[0];
    let to = args[1];

    if (pointsVal <= 0 ){
        throw new Error("Points to be issued must be > 0");
    }

    let leadWallet = await stub.getState("leadWallet");
    leadWallet = JSON.parse(leadWallet.toString());

    if (leadWallet.balance <= pointsVal) {
        throw new Error(`Lead wallet balance ${leadWallet.balance} insufficient to issue ${pointsVal} points`);
    }

    let toWallet = await stub.getState(to);
    if (toWallet.toString().length <= 0){
        throw new Error("To Wallet does not exist");
    }
    toWallet = JSON.parse(toWallet.toString());

    leadWallet.balance -= pointsVal;
    toWallet.balance = parseInt(toWallet.balance) + parseInt(pointsVal);

    try{
        await stub.putState("leadWallet", Utils.jsonToBuffer(leadWallet));
        await stub.putState(to, Utils.jsonToBuffer(toWallet));
    } catch (error) {
        return shim.error(error);
    }

    let payload = {}

    payload.lead_wallet_body = leadWallet;
    payload.toWallet = toWallet;

    return Buffer.from(JSON.stringify(payload), 'utf8');
  }
  
//   async transfer(stub, args) {
      
// }

  async getCustomerWallet(stub, args) {
    logger.info("============== Query Account Called ==============");
    let cid = new ClientIdentity(stub);
    let x509 = cid.getX509Certificate();
    let account_id = x509.issuer.organizationName.toString() + "." + x509.subject.commonName.toString();
    let account_key = "customer_account." + account_id;
    let wallet_key = "customer_wallet." + account_id;
    
    let jsonResp = {};

    let walletBytes = await stub.getState(wallet_key);
    if (walletBytes.toString() == ""){
        jsonResp.error = "Account for identity has not been created" ; 
        throw new Error(JSON.stringify(jsonResp));
    }

    let accountBytes = await stub.getState(account_key);

    jsonResp.wallet = JSON.parse(walletBytes.toString());
    jsonResp.wallet_id = wallet_key;
    jsonResp.account = JSON.parse(accountBytes.toString());
    jsonResp.account_id = account_key;

    logger.info('Query Response:');
    logger.info(jsonResp);
    return Buffer.from(JSON.stringify(jsonResp), 'utf-8');
}

  // query callback representing the query of a chaincode
  async query(stub, args) {
    if (args.length != 1) {
      throw new Error('Incorrect number of arguments. Expecting name of the person to query')
    }

    let jsonResp = {};
    let A = args[0];

    // Get the state from the ledger
    let Avalbytes = await stub.getState(A);
    if (!Avalbytes) {
      jsonResp.error = 'Failed to get state for ' + A;
      throw new Error(JSON.stringify(jsonResp));
    }

    jsonResp.name = A;
    jsonResp.amount = Avalbytes.toString();
    console.info('Query Response:');
    console.info(jsonResp);
    return Buffer.from(JSON.stringify(jsonResp), 'utf8');
  }



  async pingCustomer(stub, args) {
    logger.info("================ Ping Customer Called ================");        
    let cid = new ClientIdentity(stub);
    let x509 = cid.getX509Certificate();
    let account_id = x509.issuer.organizationName.toString() + "." + x509.subject.commonName.toString();
    let account_key = "customer_account." + account_id;
    let wallet_key = "customer_wallet." + account_id; 

    let Val = await stub.getState(account_key);

    logger.info("Val returned is: ", Val.toString());

    let answer = {};
    answer.payload = Val;
    answer.payloadString = Val.toString();

    return Buffer.from(JSON.stringify(answer), 'utf8');
}

async ping(stub, args) {
    const business_role = new ClientIdentity(stub).getAttributeValue("MINT");
    logger.info("ping called", " by ", business_role.toString());
    let answer = {}
    if (business_role.toString() == "YES"){
        answer.ping = 'pong mint';
    }else {
        answer.ping = 'pong' ;
    }
    return Buffer.from(JSON.stringify(answer), 'utf8');
  }

  async queryAccount(stub, args) {
    logger.info("============== Query Account Called ==============");
    const business_role = new ClientIdentity(stub).getAttributeValue("BUSINESS_ROLE");
    // Validations.confirmAttribute('customer', business_role);


    let cid = new ClientIdentity(stub);
    let x509 = cid.getX509Certificate();
    let fingerPrint = x509.fingerPrint;
    let account_id = x509.issuer.organizationName.toString() + "." + x509.subject.commonName.toString();
    let account_key = "customer_account." + account_id;
    let wallet_key = "customer_wallet." + account_id; 

    let jsonResp = {};

     // Get the state from the ledger
    let Avalbytes = await stub.getState(account_key);
    if (!Avalbytes) {
      jsonResp.error = 'Failed to get state for ' + account_key;
      throw new Error(JSON.stringify(jsonResp));
    }

    let Bvalbytes = await stub.getState(wallet_key);
    if (!Bvalbytes) {
      jsonResp.error = 'Failed to get state for ' + wallet_key;
      throw new Error(JSON.stringify(jsonResp));
    }

    jsonResp.account = account_key;
    jsonResp.account_body = Avalbytes.toString();
    jsonResp.wallet = wallet_key;
    jsonResp.wallet_body = Bvalbytes.toString();
    console.info('Query Response:');
    console.info(jsonResp);
    return Buffer.from(JSON.stringify(jsonResp), 'utf8');
}

};

shim.start(new cc());