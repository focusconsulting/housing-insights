(function(){

	var expandCounter,
		expandArray,
		collapseArray,
		expandAllObject,
		collapseAllObject;

	document.querySelectorAll('.down-arrow-button').forEach(function(element){
		element.addEventListener('click', expand);
	});

	document.querySelector('.accordion-collapser').addEventListener('click', expandAll);

	function expand(e, element){};

	function collapse(e, element){};

	function accordion(e, element, object){};

	function expandAll(e, element){};

	function collapseAll(e, element){};

	function accordionAll(e, element, object){};

}())