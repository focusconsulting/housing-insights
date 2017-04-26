// attributesObj includes the key 'chart
function UserSelectionComponent(attributesObj){
  this.makePublic = function() {
    PubSub.publish("message!", { }, false, false);
  } 
}

// One possibility: individual views include UserSelectionComponents by invoking the
// constructor. Since this wouldn't be a single page app, the USCs wouldn't exist across
// multiple pages unless constructed anew.