var roundToDisplay = -1;
var VIEWPOINT="BJ";

function prettyFormat(cards)
{
	for (i = cards.length - 4; i >= 0; i -= 2)
	{
		if (strEq(cards[i], cards[i+2]) && strEq(cards[i+1], cards[i+3]))
		{
			b = cards.substring(0,i);
			c = cards.substring(i,i+4);
			d = cards.substring(i+4);
			cards = b.concat(" ").concat(c).concat(" ").concat(d);
		}
	}
	return cards
}

function prettyFormat2(cards)
{
	for (i = cards.length -2; i>=2; i-=2)
	{
		if (!strEq(cards[i], cards[i-2]))
		{
			cards = cards.substring(0,i).concat("\n").concat(cards.substring(i));
		}
	}
	return cards;
}

function changeViewPointClockwise()
{
	if (VIEWPOINT=="BJ") { VIEWPOINT="SJ"; }
	else if (VIEWPOINT=="SJ") { VIEWPOINT="DJ"; }
	else if (VIEWPOINT=="DJ") { VIEWPOINT="XJ"; }
	else if (VIEWPOINT=="XJ") { VIEWPOINT="BJ"; }
	else { alert("VIEWPOINT error"); }

	displayRound(roundToDisplay);
}

function changeViewPointCounterClockwise()
{
	if (VIEWPOINT=="BJ") { VIEWPOINT="XJ"; }
	else if (VIEWPOINT=="XJ") { VIEWPOINT="DJ"; }
	else if (VIEWPOINT=="DJ") { VIEWPOINT="SJ"; }
	else if (VIEWPOINT=="SJ") { VIEWPOINT="BJ"; }
	else { alert("VIEWPOINT error"); }

	displayRound(roundToDisplay);
}


function reset()
{
	resetModel();
	displayRound(-1);
	roundToDisplay = 0;
}

function play()
{
	// now same as forward1round, further it will be different.
	forward1round();
}

function backward1round()
{
	roundToDisplay --;
	modelBackward1Round(roundToDisplay);

	// need to sub by 1 again.
	roundToDisplay --;
	if (displayRound(roundToDisplay))
	{
		roundToDisplay++;
	}
	else
	{
		reset();
	}
}

function forward1round()
{
	modelForward1Round(roundToDisplay);

	if (displayRound(roundToDisplay))
	{
		roundToDisplay++;
	}
}
function displayRound(iRound)
{
	if (iRound >= SXD.length)
	{
		displayGameEnd();
		return false;
	}

	if (iRound < -1)
	{
		return false;
	}

	if (VIEWPOINT=="BJ") { return displayRoundCore(iRound, "我", BJ, "下家", XJ, "对家", DJ, "上家", SJ, MYCARDS, XJCARDS, DJCARDS, SJCARDS); }
	else if (VIEWPOINT=="XJ") { return displayRoundCore(iRound, "下家", XJ, "对家", DJ, "上家", SJ, "我", BJ, XJCARDS, DJCARDS, SJCARDS, MYCARDS); }
	else if (VIEWPOINT=="DJ") { return displayRoundCore(iRound, "对家", DJ, "上家", SJ, "我", BJ, "下家", XJ, DJCARDS, SJCARDS, MYCARDS, XJCARDS); }
	else if (VIEWPOINT=="SJ") { return displayRoundCore(iRound, "上家", SJ, "我", BJ, "下家", XJ, "对家", DJ, SJCARDS, MYCARDS, XJCARDS, DJCARDS); }
	else { alert("VIEWPOINT error"); }
}

