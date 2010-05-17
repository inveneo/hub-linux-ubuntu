// Localization

var langs = new Object;

function apply_lang(lang){
	var f = document.getElementsByClassName('lclzn');
	for(var i=0; i < f.length ; i++){
		var tmp = f[i].innerHTML.strip().split(",");
		f[i].innerHTML = langs[tmp[0]][lang][tmp[1]] ;
	} 
}

// localization for users.html in english
	langs['users']= new Object;
	langs['users'].en = new Array;
	langs['users'].en[0] = "User and Phone Configuration";
	langs['users'].en[1] = "";
	langs['users'].en[2] = "";


