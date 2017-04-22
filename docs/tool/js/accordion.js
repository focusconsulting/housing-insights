(function(){

	var expandCounter = 0,
		expandArray = { height: "auto", button: "up-arrow-button", remove: expand, add: collapse, threshold: 4, call: expandAll },
		collapseArray = { height: "0px", button: "down-arrow-button", remove: collapse, add: expand, threshold: 0, call: collapseAll },
		expandAllObject = { text: "Collapse All", remove: expandAll, add: collapseAll, call: expand },
		collapseAllObject = { text: "Show All", remove: collapseAll, add: expandAll, call: collapse };

	document.querySelectorAll('.down-arrow-button').forEach(function(element){
		element.addEventListener('click', expand);
	});

	document.querySelector('.accordion-collapser').addEventListener('click', expandAll);

	function expand(e, element){
		expandCounter ++;
		accordion(e, element, expandArray);
	};

	function collapse(e, element){
		expandCounter --;
		accordion(e, element, collapseArray);
	};

	function accordion(e, element, object){
		target = e.currentTarget || element;
		target.parentElement.parentElement.querySelector('.accordion-panel').style.height = object.height;
		target.className = object.button + " arrow-button";
		target.removeEventListener('click', object.remove);
		target.addEventListener('click', object.add);
		if (expandCounter === object.threshold){
			object.call(false, document.querySelector('.accordion-collapser'));
			expandCounter = object.threshold;
		};
	};

	function expandAll(e, element){
		accordionAll(e, element, expandAllObject);
	};

	function collapseAll(e, element){
		accordionAll(e, element, collapseAllObject);
	};

	function accordionAll(e, element, object){
		target = e.currentTarget || element;
		target.textContent = object.text;
		target.removeEventListener('click', object.remove);
		target.addEventListener('click', object.add);
		document.querySelectorAll('.arrow-button').forEach(function(button){
			object.call(false, button);
		})
	};

}())