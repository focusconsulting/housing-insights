/*Comment here helps keep Jekyll from getting confused*/
'use strict';

/*
 * MODEL **********************************
 */

var model = {
  // TODO (?) change to a module similar to State and Subscribe so that dataCollection can only be accessed
  // through functions that the module returns to the handlers
  dataCollection: {},
  loadMetaData: function () {
    var metaDataRequest = {
      url: model.URLS.metaData,
      name: "metaData",
    };
    controller.getData(metaDataRequest);
  },
  // Here's where we keep hardcoded URLs.
  //NOTE raw data sources have their urls included in the metaData
  URLS: {
    geoJSONPolygonsBase: "/tool/data/",
    metaData: "https://api.housinginsights.org/api/meta",
    filterData: "https://api.housinginsights.org/api/filter/",
    project: "https://api.housinginsights.org/api/project/",
    layerData:
      "https://api.housinginsights.org/api/zone_facts/<source_data_name>/<grouping>",
  },
};

/* STATE ********************************
 *
 * State module keeps the state object private; only access is through module-scoped functions with closure over state. We have access
 * to those functions, and thus to state, by returning them to controller.controlState.
 */

function StateModule() {
  var state = {};

  function logState() {
    console.log(state);
  }

  function getState() {
    return state;
  }

  function setState(key, value) {
    // making all state properties arrays so that previous value is held on to
    // current state to be accessed as state[key][0].
    var stateIsNew = state[key] === undefined;

    console.groupCollapsed("setState:", key, value);
    if (stateIsNew) {
      state[key] = [value];
      PubSub.publish(key, value);
      console.log("STATE CREATED", key, value);
      console.trace("Stack trace for state " + key);
    } else {
      //If it's a string or array and values are the same, stateChanged=False+
      var stateChanged = true;
      if (typeof value === "string") {
        stateChanged = state[key][0] !== value;
      } else if (Array.isArray(value) && Array.isArray(state[key][0])) {
        stateChanged = !value.compare(state[key][0]);
      } else {
        stateChanged = true; //assume it's changed if we can't verify
      }

      //Only publish if we've changed state
      if (stateChanged) {
        state[key].unshift(value);
        PubSub.publish(key, value);

        console.log("STATE CHANGE", key, value);
        console.trace("Stack trace for state " + key);
        if (state[key].length > 2) {
          state[key].length = 2;
        }
      } else {
        //TODO do we want for there to be another 'announceState' method that publishes every time it fires, even if the value remains the same??
        console.log("STATE UNCHANGED, NO PUB:", key, value);
        console.trace("Stack trace for state " + key);
      }
    }
    console.groupEnd();
  }

  function clearState(key) {
    delete state[key];
    PubSub.publish("clearState", key);
    console.log("CLEAR STATE", key);
  }
  return {
    logState: logState,
    getState: getState,
    setState: setState,
    clearState: clearState,
  };
}

/*
 * Subscriptions module for setting, canceling, and logging all PubSub subscriptions. Automatically creates token for each unique
 * plus function (string) combination so that we don't have to remember them and so that duplicate topic-function pairs
 * cannot be made.
 */

function SubscribeModule() {
  var subscriptions = {};

  function logSubs() {
    console.log(subscriptions);
  }

  function createToken(topic, fnRef) {
    var functionHash = "f" + fnRef.toString().hashCode();
    var str = topic + fnRef;
    var token = "sub" + str.hashCode();
    return {
      token: token,
      fn: functionHash,
    };
  }

  function setSubs(subsArray) {
    // subsArray is array of topic/function pair arrays
    subsArray.forEach(function (pair) {
      var topic = pair[0],
        fnRef = pair[1],
        tokenObj = createToken(topic, fnRef);

      if (subscriptions[tokenObj.fn] === undefined) {
        subscriptions[tokenObj.fn] = {};
      }
      if (subscriptions[tokenObj["fn"]][topic] === undefined) {
        subscriptions[tokenObj["fn"]][topic] = PubSub.subscribe(topic, fnRef);
      } else {
        throw "Subscription token is already in use.";
      }
    });
  }

  function cancelSub(topic, fnRef) {
    // for canceling single subscription
    var tokenObj = createToken(topic, fnRef);
    if (
      subscriptions[tokenObj.fn] !== undefined &&
      subscriptions[tokenObj["fn"]][topic] !== undefined
    ) {
      PubSub.unsubscribe(subscriptions[tokenObj["fn"]][topic]);
      delete subscriptions[tokenObj["fn"]][topic];
      if (Object.keys(subscriptions[tokenObj["fn"]]).length === 0) {
        delete subscriptions[tokenObj["fn"]];
      }
    } else {
      throw "Subscription does not exist.";
    }
  }

  function cancelFunction(fnRef) {
    var tokenObj = createToken("", fnRef);
    PubSub.unsubscribe(fnRef);
    delete subscriptions[tokenObj["fn"]];
  }

  return {
    logSubs: logSubs,
    setSubs: setSubs,
    cancelSub: cancelSub,
    cancelFunction: cancelFunction,
  };
}

/*
 * CONTROLLER ******************************
 */

var controller = {
  controlState: StateModule(),
  controlSubs: SubscribeModule(),
  init: function () {
    setSubs([
      ["switchView", controller.switchView],
      ["switchView", router.pushViewChange],
    ]);
    if (router.initialView === "building") {
      setState("activeView", projectView);
      projectView.init(router.buildingID); // parameter distinguishes actions taken in projectView.init()
    } else {
      setState("activeView", mapView);
      mapView.init();
    }
  },
  // dataRequest is an object with the properties 'name', 'url' and 'callback'. The 'callback' is a function
  // that takes as an argument the data returned from getData.
  getData: function (dataRequest) {
    var retryCount = 0;
    if (model.dataCollection[dataRequest.name] === undefined) {
      // if data not in collection
      function recursive() {
        d3.json(dataRequest.url, function (error, data) {
          if (error) {
            console.log(error);
            if (retryCount < 2) {
              console.log("trying again " + retryCount);
              recursive();
              retryCount++;
            } else {
              console.log("giving up");
              setState(
                "getDataError." +
                  dataRequest.name +
                  "." +
                  error.currentTarget.status,
                true
              );
            }
          } else {
            if (data.objects !== null) {
              model.dataCollection[dataRequest.name] = data;
              setState("dataLoaded." + dataRequest.name, true);
              if (dataRequest.callback !== undefined) {
                // if callback has been passed in
                dataRequest.callback(data);
              }
            } else {
              //This approach suggests that either the caller (via callback) or the subscriber (via dataLoaded state change)
              //should appropriately handle a null data return. If they don't handle it, they'll probably get errors anyways.
              setState("dataLoaded." + dataRequest.name, false);
              if (dataRequest.callback !== undefined) {
                // if callback has been passed in
                dataRequest.callback(data);
              }
            }
          }
        });
      }
      recursive();
    } else {
      // TODO publish that data is available every time it's requested or only on first load?
      if (dataRequest.callback !== undefined) {
        // if callback has been passed in
        dataRequest.callback(model.dataCollection[dataRequest.name]);
      }
    }
  }, // bool
  appendPartial: function (partialRequest, context) {
    partialRequest.container = partialRequest.container || "body-wrapper";
    d3.html(
      "tool/partials/" + partialRequest.partial + ".html",
      function (fragment) {
        if (partialRequest.transition) {
          fragment
            .querySelector(".main-view")
            .classList.add("transition-right");
          setTimeout(function () {
            document
              .querySelector(".transition-right")
              .classList.remove("transition-right");
          }, 200);
        }
        document.getElementById(partialRequest.container).appendChild(fragment);
        if (partialRequest.callback) {
          partialRequest.callback.call(context); // call the callbBack with mapView as the context (the `this`)
        }
      }
    );
  },
  joinToGeoJSON: function (source_data_name, grouping) {
    model.dataCollection[grouping].features.forEach(function (feature) {
      var zone = feature.properties.NAME;
      var dataKey = source_data_name + "_" + grouping;
      var zone_entry = model.dataCollection[dataKey].objects.find(function (
        obj
      ) {
        return obj.zone === zone;
      });
      //Handle case of a missing entry in the API
      if (zone_entry == undefined) {
        zone_entry = {};
        zone_entry[source_data_name] = null;
      }

      feature.properties[source_data_name] = zone_entry[source_data_name];
    });
    setState("joinedToGeo." + source_data_name + "_" + grouping, {
      overlay: source_data_name,
      grouping: grouping,
      activeLayer: grouping,
    }); //TODO change joinedToGeo to not need activeLayer

    // e.g. joinedToGeo.crime_neighborhood, {overlay:'crime',grouping:'neighborhood_cluster',activeLayer:'neighborhood_cluster'}
  },
  convertToGeoJSON: function (data) {
    // thanks, Rich !!! JO. takes non-geoJSON data with latititude and longitude fields
    // and returns geoJSON with the original data in the properties field
    var features = data.objects.map(function (element) {
      return {
        type: "Feature",
        geometry: {
          type: "Point",
          coordinates: [+element.longitude, +element.latitude],
        },
        properties: element,
      };
    });
    return {
      type: "FeatureCollection",
      features: features,
    };
  },
  // ** NOTE re: classList: not supported in IE9; partial support in IE 10
  switchView: function (msg, data) {
    if (data === undefined) {
      location.reload();
      return;
    }
    console.log(msg, data);
    var container = document.getElementById(getState().activeView[0].el);
    container.classList.add("fade");
    console.log(data === getState().activeView[1]);
    setTimeout(function () {
      container.classList.remove("fade");
      container.classList.add("inactive");

      if (data !== getState().activeView[1]) {
        // if not going back
        container.classList.add("transition-left");
        data.init();
        controller.backToggle = 0;
      } else {
        if (controller.backToggle === 0) {
          container.classList.add("transition-right");
        } else {
          container.classList.add("transition-left");
        }
        controller.backToggle = 1 - controller.backToggle;
        document.getElementById(data.el).classList.remove("inactive");
        document.getElementById(data.el).classList.remove("transition-left");
        document.getElementById(data.el).classList.remove("transition-right");

        data.onReturn();
      }
      setState("activeView", data);
    }, 500);
  },
  backToggle: 0,
  goBack: function (hideFromHistory) {
    setState("switchView", getState().activeView[1]);
  },
};

/* Aliases */

var setState = controller.controlState.setState,
  getState = controller.controlState.getState,
  logState = controller.controlState.logState,
  clearState = controller.controlState.clearState;

var setSubs = controller.controlSubs.setSubs,
  logSubs = controller.controlSubs.logSubs,
  cancelSub = controller.controlSubs.cancelSub,
  cancelFunction = controller.controlSubs.cancelFunction;

/*
 * HELPERS *********************** (polyfills moved to separate file to be more explicit)
 */

//TODO should these be wrapped up into a 'helpers' namespace? Or maybe the new utils section?

// HELPER roundTo
Math.roundTo = function (start, tensExample) {
  var numberToRound = start / tensExample;
  return Math.round(numberToRound) * tensExample;
};

var getFieldFromMeta = function (table, sql_name) {
  var meta = model.dataCollection["metaData"]; //todo this assumes the data is available already to avoid callback - relies on calling function to request meta first
  var tableFields = meta[table]["fields"];

  for (var i = 0; i < tableFields.length; i++) {
    if (tableFields[i]["sql_name"] == sql_name) {
      return tableFields[i];
    }
  }
  return null;
};
// HELPER get parameter by name
var getParameterByName = function (name, url) {
  // HT http://stackoverflow.com/a/901144/5701184
  if (!url) {
    url = window.location.href;
  }
  name = name.replace(/[\[\]]/g, "\\$&");
  var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
    results = regex.exec(url);
  if (!results) return null;
  if (!results[2]) return "";
  return decodeURIComponent(results[2].replace(/\+/g, " "));
};

// HELPER array.move()

Array.prototype.move = function (old_index, new_index) {
  // HT http://stackoverflow.com/questions/5306680/move-an-array-element-from-one-array-position-to-another
  // native JS for moving around array items
  // used e.g. in pie-chart.js to always move the all-zone option to the top
  while (old_index < 0) {
    old_index += this.length;
  }
  while (new_index < 0) {
    new_index += this.length;
  }
  if (new_index >= this.length) {
    var k = new_index - this.length;
    while (k-- + 1) {
      this.push(undefined);
    }
  }
  this.splice(new_index, 0, this.splice(old_index, 1)[0]);
  return this; // for testing purposes
};

//array.compare(otherArray) //HT https://stackoverflow.com/questions/6229197/how-to-know-if-two-arrays-have-the-same-values
Array.prototype.compare = function (testArr) {
  if (this.length != testArr.length) return false;
  if (this.length === 0 && testArr.length === 0) return true;
  console.log("in compare");
  console.log(this);
  for (var i = 0; i < testArr.length; i++) {
    if (this[i] !== testArr[i]) {
      return false;
    }
  }
  return true;
};

// HELPER String.hashCode()

String.prototype.hashCode = function () {
  var hash = 0,
    i,
    chr,
    len;
  if (this.length === 0) return hash;
  for (i = 0, len = this.length; i < len; i++) {
    chr = this.charCodeAt(i);
    hash = (hash << 5) - hash + chr;
    hash |= 0; // Convert to 32bit integer
  }
  return hash;
};

// HELPER String.cleanString()

String.prototype.cleanString = function () {
  // lowercase and remove punctuation and replace spaces with hyphens; delete punctuation
  return this.replace(/[ \\\/]/g, "-")
    .replace(/['"”’“‘,\.!\?;\(\)&]/g, "")
    .toLowerCase();
};

/* Go! */

controller.init();
