var request = require('supertest');
var should = require('chai').should();

const url = 'http://localhost:9991/group'
const url_member = 'http://localhost:9991/group/member'
const url_message = 'http://localhost:9991/group/messages'
const url_user_message = 'http://localhost:9991/group/user_messages'
const url_login = 'http://localhost:9991/accounts/login/'

var test1_sessionid
var yicong_sessionid
//login two users
describe('get yicong sessionid', function(){
    it('dev_login POST', function(done){
        request(url_login)
        .post('local/')
        .set('Content-type','application/x-www-form-urlencoded')
        .send('direct_email=yicong%40tijee.com')
        .expect(200)
        .end(function(err, res){
            done();
            yicong_sessionid = res.header['set-cookie']
        })
    })
})

describe('get test1 sessionid', function(){
    it('pwd_login POST', function(done){
        request(url_login)
        .post('')
        .set('Content-type','application/x-www-form-urlencoded')
        .set('Cookie','csrftoken=9dpUvEjepCkt7zd8KroVekd7DzQSdpYU')
        .send('csrfmiddlewaretoken=9dpUvEjepCkt7zd8KroVekd7DzQSdpYU&username=test1%40tijee.com&password=tijee%40test1')
        .expect(200)
        .end(function(err, res){
            done();
            test1_sessionid = res.header['set-cookie']
        })
    })
})

//user = yicong@tijee.com
describe('group class tests', function(){
    var name = "test_post_2"
    var newname = 'test_change_name'
    it('group GET', function(done){
        request(url)
        .get('')
        .set('Cookie', yicong_sessionid)
        .expect(200)
        .end(function(err, res){
            res.body.result.should.be.equal("success");
            done();
        })
    })

    it('group POST', function(done){
        request(url)
        .post('')
        .set('Cookie', yicong_sessionid)
        .send({ "name":name})
        .end(function(err, res){
            res.body.name.should.be.equal(name)
            done();
        })
    })
    
    it('group DELETE', function(done){
        request(url)
        .delete('')
        .set('Cookie', yicong_sessionid)
        .send({"name":name})
        .end(function(err, res){
            res.body.result.should.be.equal("success")
            done();
        })
    })

    it('group PATCH', function(done){
        request(url)
        .patch('')
        .set('Cookie', yicong_sessionid)
        .send({"group_id":5, "newname":newname})
        .end(function(err, res){
            res.body.result.should.be.equal("error")
            done();
        })
    })
})


 //tests for group members operations
//user = yicong@tijee.com  GET_yes ADD_yes DELETE_yes
//user = test1@tijee.com    GET_yes ADD_no DELETE_no
describe('group members tests', function(){
    var user_id = 22
    var group_id = 37
    it('members GET owner', function(done){
        request(url_member)
        .get(`/${group_id}`)
        .set('Cookie', yicong_sessionid)
        .expect(200)
        .end(function(err, res){
            res.body.result.should.be.equal("success");
            done();
        })
    })

    it('members GET non-member ', function(done){
        request(url_member)
        .get(`/${group_id}`)
        .set('Cookie', test1_sessionid)
        .expect(200)
        .end(function(err, res){
            res.body.result.should.be.equal("error");
            done();
        })
    })

    it('member ADD owner', function(done){
        request(url_member)
        .post('')
        .set('Cookie', yicong_sessionid)
        .send({"group_id":group_id, "user_id":user_id})
        .end(function(err, res){
            res.body.result.should.be.equal("success")
            done();
        })
    })

    it('members GET member', function(done){
        request(url_member)
        .get(`/${group_id}`)
        .set('Cookie', test1_sessionid)
        .expect(200)
        .end(function(err, res){
            res.body.result.should.be.equal("success");
            done();
        })
    })

    it('member ADD member', function(done){
        request(url_member)
        .post('')
        .set('Cookie', test1_sessionid)
        .send({"group_id":group_id, "user_id":user_id})
        .end(function(err, res){
            res.body.result.should.be.equal("error")
            done();
        })
    })

    it('members GET', function(done){
        request(url_member)
        .get(`/${group_id}`)
        .set('Cookie', yicong_sessionid)
        .expect(200)
        .end(function(err, res){
            res.body.members.length.should.be.equal(2);
            done();
        })
    })

    it('member DELETE member', function(done){
        request(url_member)
        .delete('')
        .set('Cookie', test1_sessionid)
        .send({"group_id":group_id, "user_id":user_id})
        .end(function(err, res){
            res.body.result.should.be.equal("error")
            done();
        })
    })

    it('member DELETE owner', function(done){
        request(url_member)
        .delete('')
        .set('Cookie',yicong_sessionid)
        .send({"group_id":group_id, "user_id":user_id})
        .end(function(err, res){
            res.body.result.should.be.equal("success")
            done();
        })
    })

    it('members GET', function(done){
        request(url_member)
        .get(`/${group_id}`)
        .set('Cookie', yicong_sessionid)
        .expect(200)
        .end(function(err, res){
            res.body.members.length.should.be.equal(1);
            done();
        })
    })
})

//tests for group message operations 
//user_send = yicong@tijee.com
//user_receive = test1@tijee.com
describe('group messages tests', function(){
    var user_id = 22
    var group_id = 28
    var content = "sending test 1."
    //yicong@tijee.com  send the message
    it('messages POST', function(done){
        request(url_message)
        .post('/send')
        .set('Cookie', yicong_sessionid)
        .send({"message_type_name":"group", "recipient_id":group_id, "message_content":content,"subject_name":"test"})
        .end(function(err, res){
            res.body.result.should.be.equal("success")
            done();
        })
    })

    it('messages GET', function(done){
        request(url_message)
        .get(`/${group_id}`)
        .expect(200)
        .end(function(err, res){
            res.body.messages[0].content.should.be.equal(content);
            done();
        })
    })

    //test1@tijee.com receive the message
    it('user_messages GET', function(done){
        request(url_user_message)
        .get('/?anchor=10000&num_before=0&num_after=0')//edit here to change number of messages you get
        .set('Content-Type','application/json')
        .set('Cookie', test1_sessionid)
        .expect(200)
        .end(function(err, res){
            res.body.messages[0].content.should.be.equal('<p>'+content+'</p>');
            done();
        })
    })

    //yicong@tijee.com delete all group message
    it('messages DELETE', function(done){
        request(url_message)
        .delete('/delete')
        .send({"group_id":group_id})
        .set('Cookie', yicong_sessionid)
        .end(function(err, res){
            res.body.msg.should.be.equal("All group messages are deleted!")
            done();
        })
    })

    it('messages GET', function(done){
        request(url_message)
        .get(`/${group_id}`)
        .expect(200)
        .end(function(err, res){
            res.body.messages.length.should.be.equal(0);
            done();
        })
    })
    
}) 