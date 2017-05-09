//Suggest appending **everything** to the app variable
var FooChart = function(data,el,field,sortField,asc) { 
    baseChart.call(this,data,el,field,sortField,asc); 
    this.extendPrototype(app.genericCharts.foo.prototype, FooExtension);
}

FooChart.prototype = Object.create(FooChart.prototype);

var FooExtension = { 

  //Properties of the chart. counter is just a dummy example
  counter: 0,

  //Expect all charts to have these methods
  setup: function(el, field, width, height){
    return "<p>Foo Chart: " + this.counter + "</p>"
  },
  update: function(){
    this.counter++
    return "<p>Foo Chart: " + this.counter + "</p>"
  },

  legend: function(){
    return "<p>I'm a legend!</p>"
  },

  //can add anything else specific that the chart needs to do its thing
  FooSpecificHelperFunctions: function(){
    console.log("could do something")
  }
};
