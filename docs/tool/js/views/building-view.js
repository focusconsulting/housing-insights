"use strict";

var buildingView = {
    el:'building-view',
    init: function(){                                               //p3 true -> partial slides in from right
        controller.appendPartial('building-view','body-wrapper', true);
    }

}