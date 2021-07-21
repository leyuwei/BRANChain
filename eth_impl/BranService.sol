pragma solidity >0.4.23;

contract BranService {
    
    
    // Version: 1 
    // Modified: YWLe @ 20200628
    
    
    /////////////////////////////////////
    // Constant & Variable Declaration //
    /////////////////////////////////////
    
    struct rele {                       // request element
        uint req_time;                  // timestamp
        address payable addr_user;      // address of user
        address payable addr_server;    // address of server
        string details;                 // service details
        uint price;                     // service price (per hour)
        uint serv_time;                 // service time required
        uint deposit;                   // closing cost
        bytes sig_user;                 // signature of user
        bytes sig_server;               // signature of server
        bytes32 final_hash;             // keccak256 value of this rele
    }
    
    rele private _r;                    // the only instance of structure rele 
    uint private start_time;            // the timestamp when service starts
    string private appeal_reason;       // the accuser should state the problem in detail using this string
    uint private jury_ub = 5;           // the maximum number of public jury who decide which side to punish
    uint private jury_num = 0;          // the number of juries who have voted
    uint private jury_withdraw = 0;     // the number of juries who decide to continue the service and withdraw the suit
    uint private jury_on_user = 0;      // the number of juries who decide to support the user and punish the server
    address payable public requestor;   // requestor of this contract (either be user or server)
    uint private status;                // status | 0-initiate | 1-in service | 2-close | 3-argument

    // Events: used with DApps
    event ServiceStart(uint time, address addr_user, address addr_server, uint serv_time);
    event ServicePaused(uint time, address addr_user, address addr_server, string appeal_reason);
    event ServiceRestored(uint time, address addr_user, address addr_server, uint serv_time);
    event ServiceEnded(uint time, address addr_user, address addr_server, uint serv_time);
    
    // Modifiers: used after function declarations
    // modifier onlyBefore(uint _time) { require(now < _time); _; }
    // modifier onlyAfter(uint _time) { require(now > _time); _; }
    // modifier onlyWhenDepositIsNotEnough() { require(address(this).balance < _r.deposit); _; }
    // modifier onlyWhenDepositIsEnough() { require(address(this).balance >= _r.deposit); _; }
    // modifier onlyYou(address payable _addr) { require(_addr == msg.sender); _; }
    // modifier onlyParticipants() { require(msg.sender == _r.addr_user || msg.sender == _r.addr_server); _; }
    // modifier exceptParticipants() { require(msg.sender != _r.addr_user && msg.sender != _r.addr_server); _; }
    // modifier onlyWhenServiceIsInTrouble() { require(status==3); _; }
    // modifier onlyWhenServiceIsOver() { require(status==2); _; }
    // modifier onlyWhenServiceHasComplete() { require(status==1 && now - start_time > _r.serv_time); _; }
    // modifier onlyWhenServiceIsGoing() { require(status==1); _; }
    // modifier onlyWhenServiceIsInitiated() { require(status==0); _;}
    // modifier onlyWhenReleIsFilled(rele memory _e) {
    //     // require(_e.req_time > 0);
    //     // require(_e.addr_user != address(0));
    //     // require(_e.addr_server != address(0));
    //     // require(_e.price > 0);
    //     // require(_e.serv_time > 0);
    //     // require(_e.deposit > 0);
    //     // require(_e.sig_user.length > 0);
    //     // require(_e.sig_server.length > 0);
    //     // require(_e.final_hash != 0);
    //     _;
    // }
    
    
    //////////////////////////
    // Function Declaration //
    //////////////////////////
    
    constructor(
        address payable _addr_user,
        address payable _addr_server,
        string memory _details,
        uint _price,
        uint _serv_time,
        uint _deposit,
        bytes memory _sig_user,
        bytes memory _sig_server
    ) public payable{
        requestor = msg.sender;
        // require(requestor == _addr_user || 
        //         requestor == _addr_server);                 // verify the identity of the contract creator
        // require(_deposit == _price * _serv_time);           // deposit should be correctly calculated
        // Fill in values of the current request
        _r = rele({
            req_time: now,
            addr_user: _addr_user,
            addr_server: _addr_server,
            details: _details,
            price: _price,
            serv_time: _serv_time,
            deposit: _deposit,
            sig_server: _sig_server,
            sig_user: _sig_user,
            final_hash: 0
        });
        // Verify signatures of user and server
        // The signatures must be encoded using the following codes in GETH console:
        //      bytes memory prefix = "\x19Ethereum Signed Message:\n32";
        //      bytes32 mysignature = keccak256(prefix, hash); 
        // hash is the byte32 hashed string of the 7 fields in the front of the rele struct
        // Thanks to https://ethereum.stackexchange.com/questions/26434/whats-the-best-way-to-transform-bytes-of-a-signature-into-v-r-s-in-solidity
        // bytes memory prefix = "\x19Ethereum Signed Message:\n32";
        // bytes32 user_hash = keccak256(abi.encodePacked(_r.req_time,
        //                                               _r.addr_user,
        //                                               _r.addr_server,
        //                                               _r.details,
        //                                               _r.price,
        //                                               _r.serv_time,
        //                                               _r.deposit));
        //bytes32 infohash = keccak256(abi.encodePacked(prefix, user_hash)); 
        //require(ecverify(infohash, _r.sig_user, _r.addr_user) && 
        //        ecverify(infohash, _r.sig_server, _r.addr_server));
        // The final_hash is calculated based on values of all the other fields
        _r.final_hash = keccak256(abi.encodePacked(_r.req_time,
                                                _r.addr_user,
                                                _r.addr_server,
                                                _r.details,
                                                _r.price,
                                                _r.serv_time,
                                                _r.deposit,
                                                _r.sig_user,
                                                _r.sig_server));
        status = 0;     // set stauts to zero: the contract has been initiated
    }
    
    // If the contract creator is the server, the user has to initiate another transaction to pay deposit
    function payDeposit()
        public
        payable
        // onlyYou(_r.addr_user)
        // onlyWhenServiceIsInitiated
        // onlyWhenDepositIsNotEnough
    {
        // The user should pay enough money, otherwise the service won't start
        // require (msg.value + address(this).balance >= _r.deposit);
    }
    
    function close() 
        public 
        // onlyYou(requestor)
        // onlyWhenServiceIsOver
    {
        selfdestruct(requestor);
    }
    
    function start_service()
        public
        // onlyYou(_r.addr_server)
        // onlyWhenServiceIsInitiated
        // onlyWhenDepositIsEnough
    {
        start_time = now;   // set start_time to now
        status = 1;         // set status to one: the service has begun   
        emit ServiceStart(start_time, _r.addr_user, _r.addr_server, _r.serv_time);
    }
    
    function end_service()
        public
        // onlyParticipants
        // onlyWhenServiceHasComplete
    {
        uint remains = address(this).balance - _r.deposit;
        _r.addr_server.transfer(_r.deposit);    // settlement
        _r.addr_user.transfer(remains);         // refund exceeding cryptos to the user
        remains = 0;        // set var to zero for safety concerns
        status = 2;         // set status to two: the service has finished
        emit ServiceEnded(now, _r.addr_user, _r.addr_server, _r.serv_time);
    }
    
    // Problem Handler
    // This function can only be called before service time is over
    // It can be reckon as an interruption to the service
    function appeal_service(string memory _appeal_reason)
        public
        // onlyParticipants
        // onlyWhenServiceIsGoing  // You can only file a suit when service is currently going
    {
        status = 3;         // set status to three: the service has encountered some problem
        appeal_reason = _appeal_reason;
        emit ServicePaused(now, _r.addr_user, _r.addr_server, _appeal_reason);
    }
    
    // The anonymous public jury can judge the situation based on the appeal_reason
    function public_jury(bool _is_in_trouble,   // has anyone violated the rules? 
                         uint _support_side)    // if so, which side do you on? | 0-user | 1-server
        public 
        // exceptParticipants
        // onlyWhenServiceIsInTrouble
    {
        jury_num += 1;
        if (!_is_in_trouble) { jury_withdraw += 1; }
        else if (_support_side == 0) { jury_on_user += 1; }
        if (jury_withdraw >= jury_ub * 3 / 5) {
            status = 1;     // set status back to 1 and continue the service
            emit ServiceRestored(now, _r.addr_user, _r.addr_server, _r.serv_time);
        }
        if (jury_num >= jury_ub) {
            uint num_jury_participated = jury_num - jury_withdraw;
            // Punish based on majority decisions
            if (jury_on_user > num_jury_participated / 2) {
                _r.addr_user.transfer(address(this).balance);
                status = 2;
                emit ServiceEnded(now, _r.addr_user, _r.addr_server, _r.serv_time);
            } else {
                _r.addr_server.transfer(address(this).balance);
                status = 2;
                emit ServiceEnded(now, _r.addr_user, _r.addr_server, _r.serv_time);
            }
            num_jury_participated = 0;
        }
    }
    
    
    ///////////////////////
    // Toolbox Functions //
    ///////////////////////
    
    function ecrecovery(bytes32 hash, bytes memory sig) 
        internal 
        pure 
        returns (address) 
    {
        bytes32 r;
        bytes32 s;
        uint8 v;
        if (sig.length != 65) {
            return address(0);
        }
        assembly {
            r := mload(add(sig, 32))
            s := mload(add(sig, 64))
            v := and(mload(add(sig, 65)), 255)
        }
        if (v < 27) {
            v += 27;
        }
        if (v != 27 && v != 28) {
            return address(0);
        }
        return ecrecover(hash, v, r, s);
    }
    
    function ecverify(bytes32 hash, bytes memory sig, address payable signer) 
        internal 
        pure 
        returns (bool) 
    {
        return signer == ecrecovery(hash, sig);
    }

    
    function a2b(address a) 
        internal 
        pure 
        returns (bytes memory b)
    {
        assembly {
            let m := mload(0x40)
            a := and(a, 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF)
            mstore(add(m, 20), xor(0x140000000000000000000000000000000000000000, a))
            mstore(0x40, add(m, 52))
            b := m
        }
    }
    
    function s2b(string memory source) 
        internal 
        pure 
        returns (bytes memory result) 
    {
        bytes memory tempEmptyStringTest = bytes(source);
        if (tempEmptyStringTest.length == 0) {
            uint i = 0;
            return abi.encodePacked(i);
        }
        assembly {
            result := mload(add(source, 32))
        }
    }

    function u2b(uint x) 
        internal
        pure
        returns (bytes memory b) 
    {
        b = new bytes(32);
        assembly { mstore(add(b, 32), x) }
    }
}
