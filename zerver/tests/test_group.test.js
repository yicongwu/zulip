var request = require('supertest');
var should = require('chai').should();

const url = 'http://localhost:9991/group'
const url_member = 'http://localhost:9991/group/member'
const url_message = 'http://localhost:9991/group/messages'
const url_user_message = 'http://localhost:9991/group/user_messages'

describe('group class tests', function(){
    var owner_id = 18
    var name = "test_post_1"
    it('group GET', function(done){
        request(url)
        .get('')
        .expect(200)
        .end(function(err, res){
            res.body.result.should.be.equal("success");
            done();
        })
    })

    it('group POST', function(done){
        request(url)
        .post('')
        .send({"owner_id":owner_id, "name":name})
        .end(function(err, res){
            res.body.name.should.be.equal("test_post_1")
            done();
        })
    })

    it('group DELETE', function(done){
        request(url)
        .delete('')
        .send({"owner_id":owner_id, "name":name})
        .end(function(err, res){
            res.body.result.should.be.equal("success")
            done();
        })
    })

    it('group PATCH', function(done){
        request(url)
        .patch('')
        .send({"group_id":5, "newname":name})
        .end(function(err, res){
            res.body.result.should.be.equal("error")
            done();
        })
    })
})


// tests for group members operations
describe('group members tests', function(){
    var user_id = 18
    var group_id = 3
    var name = "test_post_1"
    it('members GET', function(done){
        request(url_member)
        .get(`/${group_id}`)
        .expect(200)
        .end(function(err, res){
            res.body.result.should.be.equal("success");
            done();
        })
    })

    it('member ADD', function(done){
        request(url_member)
        .post('')
        .send({"group_id":group_id, "user_id":user_id})
        .end(function(err, res){
            res.body.result.should.be.equal("success")
            done();
        })
    })

    it('member DELETE', function(done){
        request(url_member)
        .delete('')
        .send({"group_id":group_id, "user_id":user_id})
        .end(function(err, res){
            res.body.result.should.be.equal("success")
            done();
        })
    })
})

//tests for group message operations 

describe('group messages tests', function(){
    var user_id = 19
    var group_id = 28
    var content = "sending test 1."
    it('messages POST', function(done){
        request(url_message)
        .post('/send')
        .send({"user_id":user_id, "message_type_name":"group", "recipient_id":group_id, "message_content":content,"subject_name":"test"})
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

    it('user_messages GET', function(done){
        request(url_user_message)
        .get(`/${user_id}`+'?anchor=10000&num_before=0&num_after=0')//edit here to change number of messages you get
        .expect(200)
        .end(function(err, res){
            res.body.messages[0].content.should.be.equal('<p>'+content+'</p>');
            done();
        })
    })

    it('messages DELETE', function(done){
        request(url_message)
        .delete('/delete')
        .send({"group_id":group_id})
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