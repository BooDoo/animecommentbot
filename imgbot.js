#!/usr/bin/env node

var fs = require("fs");
var path = require("path");
var Twit = require("twit");
var credentials = readCredentials();
var twitter = new Twit(credentials);
var PICSPATH = "/home/boodoo/src/GitHub/animecommentbot/output"; // e.g. "/home/me/pics"
var STATUSESPATH = process.env["STATUSESPATH"];

// UTILITY: Get "random" element from array:
function pick(arr) {
  try {
    var index = Math.floor(Math.random() * arr.length);
    return arr[index];
  } catch (e) {
    return arr;
  }
}

// Pick a status text to tweet out:
function pickStatus(statuses) {
  return "";
  // statuses = statuses || readStatuses();
  // return pick(statuses);
}

// Read files in a directory, return full path for one of them:
function pickAPic(picsPath) {
  picsPath = picsPath || PICSPATH || './images';
  var picPath = pick(fs.readdirSync(picsPath));
  console.log("Picked", picPath);
  picPath = path.join(picsPath, picPath);
  return picPath;
}

function readStatuses(statusesPath) {
  statusesPath = statusesPath || STATUSESPATH || './statuses.txt';
  var statuses = fs.readFileSync(statusesPath, {encoding: 'utf8'}).split(/\r\n|\r|\n/g);
}

// Read twitter API stuff from JSON file or environment variables:
function readCredentials() {
  var credentials;

  try {
    credentials = require("./credentials.json");
  } catch(e) {
    credentials = {
      consumer_key:         process.env["CONSUMER_KEY"],
      consumer_secret:      process.env["CONSUMER_SECRET"],
      access_token:         process.env["ACCESS_TOKEN"],
      access_token_secret:  process.env["ACCESS_TOKEN_SECRET"]
    }
  }

  return credentials;
}

// Tweet with text and an image
function tweetAPic(picPath) {
  var picB64 = fs.readFileSync(picPath, {encoding: "base64"});
  twitter.post("media/upload", { media_data: picB64 }, afterUpload);
}

// After uploading the media, add status text and tweet it out:
function afterUpload(err, data) {
  if (!err) {
    var mediaId = data.media_id_string; // tell twitter which image to attach…
    var status = "" // pickStatus();          // get some text content…
    var params = { status: status, media_ids: [mediaId] }
    twitter.post("statuses/update", params, afterTweet);
  } else {
    console.error("Error uploading media:");
    console.error(err);
  }
}
 
// Success/failure notification for tweet attempt
function afterTweet(err, data) {
  if (!err) {
    console.log("I twote!")
  } else {
    console.error("I couldn't tweet:");
    console.error(err);
  }
}
 
// Do the thing:
(function main() {
  var picPath = pickAPic();
  tweetAPic(picPath);
})();
