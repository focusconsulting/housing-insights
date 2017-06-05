"use strict";

var buildingView = {
    el:'building-view',
    init: function(){                                               
        
        var partialRequest = {
            partial: this.el,
            container: null, // will default to '#body-wrapper'
            transition: true,
            callback: appendCallback
        };
        
        controller.appendPartial(partialRequest, this);
        
        function appendCallback() {
            this.onReturn();
        }
    },
     onReturn: function(){
        alert('Would load ' + getState().previewBuilding[0].id);
    }

}