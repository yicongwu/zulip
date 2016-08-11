var request = require('supertest');
var should = require('chai').should();

const url = 'http://localhost:9991/group'
const url_member = 'http://localhost:9991/group/member'

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


// tests for group members
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