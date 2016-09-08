var request = require('supertest');
var should = require('chai').should();

const url = 'http://localhost:9991/group'
const url_member = 'http://localhost:9991/group/member'
const url_message = 'http://localhost:9991/group/messages'
const url_user_message = 'http://localhost:9991/group/user_messages'
const url_dev_login = 'http://localhost:9991/accounts/login/local/'

var test1_sessionid
var yicong_sessionid
//login two users
describe('get two sessionid', function(){
    it('dev_login POST', function(done){
        request(url_dev_login)
        .post('')
        .set('Content-type','application/x-www-form-urlencoded')
        .send('direct_email=yicong%40tijee.com')
        .expect(200)
        .end(function(err, res){
            done();
            yicong_sessionid = res.header['set-cookie']
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

/*
// tests for group members operations
//user = yicong@tijee.com
describe('group members tests', function(){
    var user_id = 18
    var group_id = 37
    it('members GET', function(done){
        request(url_member)
        .get(`/${group_id}`)
        .set('Cookie','JSESSIONID=dummy; csrftoken=ZFbVD3sBBGKX6r6gS3fCHYWxzAZ7CNNC; sessionid=akluyubm5sfczc1ldljl6cnacaik3hbx')
        .expect(200)
        .end(function(err, res){
            res.body.result.should.be.equal("success");
            done();
        })
    })

    it('member ADD', function(done){
        request(url_member)
        .post('')
        .set('Cookie','JSESSIONID=dummy; csrftoken=ZFbVD3sBBGKX6r6gS3fCHYWxzAZ7CNNC; sessionid=akluyubm5sfczc1ldljl6cnacaik3hbx')
        .send({"group_id":group_id, "user_id":user_id})
        .end(function(err, res){
            res.body.result.should.be.equal("success")
            done();
        })
    })

    it('members GET', function(done){
        request(url_member)
        .get(`/${group_id}`)
        .set('Cookie','JSESSIONID=dummy; csrftoken=ZFbVD3sBBGKX6r6gS3fCHYWxzAZ7CNNC; sessionid=akluyubm5sfczc1ldljl6cnacaik3hbx')
        .expect(200)
        .end(function(err, res){
            res.body.length.should.be.equal(2);
            done();
        })
    })

    it('member DELETE', function(done){
        request(url_member)
        .delete('')
        .set('Cookie','JSESSIONID=dummy; csrftoken=ZFbVD3sBBGKX6r6gS3fCHYWxzAZ7CNNC; sessionid=akluyubm5sfczc1ldljl6cnacaik3hbx')
        .send({"group_id":group_id, "user_id":user_id})
        .end(function(err, res){
            res.body.result.should.be.equal("success")
            done();
        })
    })

    it('members GET', function(done){
        request(url_member)
        .get(`/${group_id}`)
        .set('Cookie','JSESSIONID=dummy; csrftoken=ZFbVD3sBBGKX6r6gS3fCHYWxzAZ7CNNC; sessionid=akluyubm5sfczc1ldljl6cnacaik3hbx')
        .expect(200)
        .end(function(err, res){
            res.body.length.should.be.equal(1);
            done();
        })
    })
})

//tests for group message operations 
//user_send = yicong@tijee.com
//user_receive = test1@tijee.com
describe('group messages tests', function(){
    var user_id = 19
    var group_id = 28
    var content = "sending test 1."
    //yicong@tijee.com  send the message
    it('messages POST', function(done){
        request(url_message)
        .post('/send')
        .set('Cookie','JSESSIONID=dummy; csrftoken=ZFbVD3sBBGKX6r6gS3fCHYWxzAZ7CNNC; sessionid=akluyubm5sfczc1ldljl6cnacaik3hbx')
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
        .get(`/${user_id}`+'?anchor=10000&num_before=0&num_after=0')//edit here to change number of messages you get
        .set('Cookie','csrftoken=yerrwPP6cB9jdZVydnDpD4CKPahorpns; sessionid=6seic5joectsnqy53w06smh4qetiforf; JSESSIONID=dummy')
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
        .set('Cookie','JSESSIONID=dummy; csrftoken=ZFbVD3sBBGKX6r6gS3fCHYWxzAZ7CNNC; sessionid=akluyubm5sfczc1ldljl6cnacaik3hbx')
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
}) */