#!/usr/bin/env node

var fs = require("fs");
var path = require("path");
var Twit = require("twit");
var _ = require("lodash");
var credentials = readCredentials();
var twitter = new Twit(credentials);

var QUEUE_PATH = './queue.txt';
var QUEUE_SEPARATOR = '=====';

// UTILITY: Get "random" element from array, destructively:
function sampleSplice(arr) {
  try {
    var index = Math.floor(Math.random() * arr.length);
    return arr.splice(index, 1)[0];
  } catch (e) {
    console.error("Error splicing; returning provided array as-is");
    return arr;
  }
}

function splitQueueItem(item) {
  var separator = QUEUE_SEPARATOR || '=====';
  return item.split(separator);
}

function joinQueueItem(item) {
  var separator = QUEUE_SEPARATOR || '=====';
  return item.join(separator);
}

function serializeQueue(items, separator) {
  separator = separator || QUEUE_SEPARATOR || '=====';
  return items.map(joinQueueItem).join("\n");
}

function readQueue(queuePath) {
  queuePath = queuePath || QUEUE_PATH || './queue.txt';
  var queue = fs.readFileSync(queuePath, {encoding: 'utf8'}).split(/\r\n|\r|\n/g);
  queue = _.without(queue, "");
  queueItems = queue.map(splitQueueItem);
  console.log("Read", queueItems.length, "items from", queuePath);
  return queueItems;
}

function writeQueue(items, queuePath, separator) {
  queuePath = queuePath || QUEUE_PATH || './queue.txt';
  separator = separator || QUEUE_SEPARATOR || '=====';
  fs.writeFileSync(queuePath, serializeQueue(items), 'utf8');
  console.log("Wrote", items.length, "items to", queuePath);
  return items;
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
function tweetAPic(picPath, status) {
  var picB64 = fs.readFileSync(picPath, {encoding: "base64"});
  var tweetMe = _.partialRight(afterUpload, status);
  twitter.post("media/upload", { media_data: picB64 }, tweetMe);
}

// After uploading the media, add status text and tweet it out:
function afterUpload(err, data, res, status) {
  if (!err) {
    var mediaId = data.media_id_string; // tell twitter which image to attach…
    status = status || ""               // some text content…
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
  var queueItems = readQueue();             // Read image/caption combos (queue.txt)
  var thisItem = sampleSplice(queueItems);  // Take a random line and remove it from the list
  console.log("Working with:\n\t=>",
              thisItem[0], "\n\t===>",
              thisItem[1]);
  tweetAPic(thisItem[0], thisItem[1]);      // Tweet the image along with associated caption
  fs.unlinkSync(thisItem[0]);               // Delete the tweeted image
  writeQueue(queueItems);                   // Re-write queue.txt with this line removed
})();
