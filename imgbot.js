#!/usr/bin/env node

var fs = require("fs");
var path = require("path");
var Twit = require("twit");
var _ = require("lodash");
var credentials = readCredentials();
var twitter = new Twit(credentials);

var QUEUE_PATH = './queue.txt';
var QUEUE_SEPARATOR = '=====';

// HACK:
// Overwrite the twitter.prototype._buildReqOpts to support media/metadata/create.json

twitter._buildReqOpts = function buildReqOpts(method, path, params, isStreaming, callback) {
  var helpers = require("twit/lib/helpers");
  var endpoints = require("twit/lib/endpoints");
  var FORMDATA_PATHS = [
    'media/upload',
    'account/update_profile_image',
    'account/update_profile_background_image',
  ];
  var self = this
  if (!params) {
    params = {}
  }
  // clone `params` object so we can modify it without modifying the user's reference
  var paramsClone = JSON.parse(JSON.stringify(params))
  // convert any arrays in `paramsClone` to comma-seperated strings
  var finalParams = this.normalizeParams(paramsClone)
  delete finalParams.twit_options

  // the options object passed to `request` used to perform the HTTP request
  var reqOpts = {
    headers: {
      'Accept': '*/*',
      'User-Agent': 'twit-client'
    },
    gzip: true,
    encoding: null,
  }

  if (typeof self.config.timeout_ms !== 'undefined') {
    reqOpts.timeout = self.config.timeout_ms;
  }

  try {
    // finalize the `path` value by building it using user-supplied params
    path = helpers.moveParamsIntoPath(finalParams, path)
  } catch (e) {
    callback(e, null, null)
    return
  }

  if (isStreaming) {
    // This is a Streaming API request.

    var stream_endpoint_map = {
      user: endpoints.USER_STREAM,
      site: endpoints.SITE_STREAM
    }
    var endpoint = stream_endpoint_map[path] || endpoints.PUB_STREAM
    reqOpts.url = endpoint + path + '.json'
  } else {
    // This is a REST API request.

    if (path === 'media/upload') {
      // For media/upload, use a different entpoint and formencode.
      reqOpts.url = endpoints.MEDIA_UPLOAD + 'media/upload.json';
    } else if (path === 'media/metadata/create') {
      reqOpts.url = endpoints.MEDIA_UPLOAD + 'media/metadata/create.json';
      reqOpts.json = true;
      reqOpts.body = JSON.parse(JSON.stringify(
        {media_id: finalParams.media_id, alt_text: finalParams.alt_text}
      ));
      delete finalParams['media_id'];
      delete finalParams['alt_text'];
    } else {
      reqOpts.url = endpoints.REST_ROOT + path + '.json';
    }

    if (FORMDATA_PATHS.indexOf(path) !== -1) {
      reqOpts.headers['Content-type'] = 'multipart/form-data';
      reqOpts.form = finalParams;
       // set finalParams to empty object so we don't append a query string
      // of the params
      finalParams = {};
    } else {
      reqOpts.headers['Content-type'] = 'application/json';
    }

  }

  if (Object.keys(finalParams).length) {
    // not all of the user's parameters were used to build the request path
    // add them as a query string
    var qs = helpers.makeQueryString(finalParams)
    reqOpts.url += '?' + qs
  }

  if (!self.config.app_only_auth) {
    // with user auth, we can just pass an oauth object to requests
    // to have the request signed
    var oauth_ts = Date.now() + self._twitter_time_minus_local_time_ms;

    reqOpts.oauth = {
      consumer_key: self.config.consumer_key,
      consumer_secret: self.config.consumer_secret,
      token: self.config.access_token,
      token_secret: self.config.access_token_secret,
      timestamp: Math.floor(oauth_ts/1000).toString(),
    }

    callback(null, reqOpts);
    return;
  } else {
    // we're using app-only auth, so we need to ensure we have a bearer token
    // Once we have a bearer token, add the Authorization header and return the fully qualified `reqOpts`.
    self._getBearerToken(function (err, bearerToken) {
      if (err) {
        callback(err, null)
        return
      }

      reqOpts.headers['Authorization'] = 'Bearer ' + bearerToken;
      callback(null, reqOpts)
      return
    })
  }
}


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
function tweetAPic(picPath, status, altText) {
  var picB64 = fs.readFileSync(picPath, {encoding: "base64"});
  var tweetMe = _.partialRight(afterUpload, status, altText, afterTagging);
  twitter.post("media/upload", { media_data: picB64 }, tweetMe);
}

function tweetAVid(vidPath, status) {
  var tweetMe = _.partialRight(afterUpload, status);
  twitter.postMediaChunked({file_path: vidPath}, tweetMe);
}

// After uploading the media, add status text and tweet it out:
function afterUpload(err, data, res, status, altText, next) {
  if (err) {
    console.error("Error uploading media:");
    console.error(err);
  } else {
    var mediaId = data.media_id_string; // tell twitter which image to attach…
    status = status   || "";            // some text content…
    altText = altText || status;        // and some alt text
    var params = { status: status, media_ids: [mediaId] };
    var doNext = _.partialRight(next, params, afterTweet); // for callback after metatagging...
    if (altText) {
      twitter.post("media/metadata/create", {media_id: mediaId, alt_text: {"text": altText} }, doNext);
    } else {
      console.log("No alt text, skipping...");
      doNext(err, data, res);
    }
  }
}

function afterTagging(err, data, res, params, next) {
  if (err) {
    console.error("Error adding metadata");
    console.error(err);
  } else {
    twitter.post("statuses/update", params, next);
  }
}

// Success/failure notification for tweet attempt
function afterTweet(err, data) {
  if (err) {
    console.error("I couldn't tweet:");
    console.error(err);
  } else {
    console.log("I twote!")
  }
}

// Do the thing:
(function main() {
  var queueItems = readQueue();             // Read image/caption combos (queue.txt)
  var thisItem = sampleSplice(queueItems);  // Take a random line and remove it from the list
  if (thisItem.length < 3) {
    // if no alt_text, give null
    thisItem[2] = null;
  }
  console.log("Working with:\n\t=>",
              thisItem[0], "\n\t===>",
              thisItem[1],
              thisItem[2]);
  if (path.extname(thisItem[0]) === ".mp4") {
    tweetAVid(thisItem[0], thisItem[1]);                // Tweet video along with caption
  } else {
    tweetAPic(thisItem[0], thisItem[1], thisItem[2]);   // Tweet image along with caption and alt text
  }
  fs.unlinkSync(thisItem[0]);               // Delete the tweeted image
  writeQueue(queueItems);                   // Re-write queue.txt with this line removed
})();
