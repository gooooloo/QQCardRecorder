var basereplayurl = "replay.html"

function encodeGame(game)
{
	game = game.replace(/本家/g, "H");
	game = game.replace(/下家/g, "I");
	game = game.replace(/谁先打/g, "L");
	game = game.replace(/主牌/g, "M");
	game = game.replace(/十/g, "N");
	game = game.replace(/大王/g, "O");
	game = game.replace(/小王/g, "P");
	game = game.replace(/红/g, "R");
	game = game.replace(/梅/g, "S");
	game = game.replace(/方/g, "T");
	game = game.replace(/上家/g, "U");
	game = game.replace(/黑/g, "V");
	game = game.replace(/对家/g, "W");
	game = game.replace(/:/g, "X");
	game = game.replace(/\|/g, "Y");
	game = game.replace(/\n/g, "Z");
	return game;
}

function decodeGame(game)
{
	game = game.replace(/H/g, "本家");
	game = game.replace(/I/g, "下家");
	game = game.replace(/L/g, "谁先打");
	game = game.replace(/M/g, "主牌");
	game = game.replace(/N/g, "十");
	game = game.replace(/O/g, "大王");
	game = game.replace(/P/g, "小王");
	game = game.replace(/R/g, "红");
	game = game.replace(/S/g, "梅");
	game = game.replace(/T/g, "方");
	game = game.replace(/U/g, "上家");
	game = game.replace(/V/g, "黑");
	game = game.replace(/W/g, "对家");
	game = game.replace(/X/g, ":");
	game = game.replace(/Y/g, "|");
	game = game.replace(/Z/g, "\n");
	return game;
}


function fetchOriginalGameFromUrl()
{
	obj = {};
	querystring = location.search.substr(1); // those after charactor '?'
	arr = querystring.split('&');
	for (i in arr)
	{
		brr = arr[i].split('=');
		if (brr[0] == "ver") {obj["ver"] = brr[1];}
		if (brr[0] == "game") {obj["game"] = brr[1];}
	}

	return obj;
}

function fetchDecodedGameFromUrl()
{
	obj = fetchOriginalGameFromUrl();
	if (obj["ver"] == 1)
	{
		if (obj["game"] !== undefined) return decodeGame(obj["game"]);
	}
	return false;
}

function generateEncodedGameUrlParam(base, game)
{
	return base + "?ver=1&game="+encodeGame(game);
}

function generateRedirectUrlForReplay(game)
{
	return generateEncodedGameUrlParam(basereplayurl, game)
}
