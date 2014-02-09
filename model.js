
var SXD = "NULL";
var BJ= "NULL";
var XJ= "NULL";
var DJ= "NULL";
var SJ= "NULL";
var MYCARDS = "NULL";
var MYORIGCARDS = "NULL";
var XJCARDS = "NULL";
var XJORIGCARDS = "NULL";
var DJCARDS = "NULL";
var DJORIGCARDS = "NULL";
var SJCARDS = "NULL";
var SJORIGCARDS = "NULL";
var ZHUJIPAI="NULL";
var ZHUHUASE="NULL";

var sortList1 = "大小黑红梅方";
var sortList2 = "AKQJ十98765432";

function strEq(str1, str2)
{
	return str1.localeCompare(str2) == 0;
}

function swap(str, i, k)
{
	return str.substring(0,i).concat(str[k]).concat(str.substring(i+1, k)).concat(str[i]).concat(str.substring(k+1));
}

function sortCards(cards)
{
	for (i = 0; i < cards.length/2; i++)
	{
		for (k = i+1; k < cards.length/2; k++)
		{
			idxI = sortList1.indexOf(cards[2*i]);
			idxK = sortList1.indexOf(cards[2*k]);

			if (idxI > idxK)
			{
				cards = swap(cards, 2*i, 2*k);
				cards = swap(cards, 2*i+1, 2*k+1);
			}
			else if (idxI == idxK)
			{
				idxI1 = sortList2.indexOf(cards[2*i+1]);
				idxK1 = sortList2.indexOf(cards[2*k+1]);
				if (idxI1 > idxK1)
				{
					cards = swap(cards, 2*i, 2*k);
					cards = swap(cards, 2*i+1, 2*k+1);
				}
			}
		}
	}
	return cards;
}
function collectCards(arr)
{
	x = ""
	for (i in arr)
	{
		x = x.concat(arr[i]);
	}
	return sortCards(x);
}

function replay(history)
{
	lines = history.split("\n"); // Will separate each line into an array
	for (line in lines)
	{
		words = lines[line].split(":");
		if (words.length > 1)
		{
			words1 = words[1];
			words1 = words1.replace(/本家/g, "我");
			while (words1[words1.length-1] == '|'){words1=words1.substring(0, words1.length-1);}
			arr = words1.split("|");
			if (strEq(words[0], "SXD")){SXD=arr;}
			if (strEq(words[0], "谁先打")){SXD=arr;}
			else if (strEq(words[0], "本家")){BJ=arr;}
			else if (strEq(words[0], "下家")){XJ=arr;}
			else if (strEq(words[0], "对家")){DJ=arr;}
			else if (strEq(words[0], "上家")){SJ=arr;}
			else if (strEq(words[0], "ZP")){ZHUJIPAI=words1;}
			else if (strEq(words[0], "主牌")){ZHUJIPAI=words1;}
			else{alert("unexpected words[0]"+words[0]);}
		}
	}
	MYORIGCARDS = collectCards(BJ);
	MYCARDS = ""+MYORIGCARDS;
	XJORIGCARDS = collectCards(XJ);
	XJCARDS = ""+XJORIGCARDS;
	DJORIGCARDS = collectCards(DJ);
	DJCARDS = ""+DJORIGCARDS;
	SJORIGCARDS = collectCards(SJ);
	SJCARDS = ""+SJORIGCARDS;

}
function resetModel()
{
	MYCARDS = ""+MYORIGCARDS;
	XJCARDS = ""+XJORIGCARDS;
	SJCARDS = ""+SJORIGCARDS;
	DJCARDS = ""+DJORIGCARDS;
}
function undoCards(arr, cardsRound)
{
	arr = arr.concat(cardsRound);
	return sortCards(arr);
}

function redoCards(arr, cardsRound)
{
	for (i = 0; i < cardsRound.length; i+=2)
	{
		arr = arr.replace(cardsRound.substring(i, i+2), "");
	}
	return arr;
}

function modelBackward1Round(iRound)
{
	MYCARDS = undoCards(MYCARDS, BJ[iRound]);
	XJCARDS = undoCards(XJCARDS, XJ[iRound]);
	DJCARDS = undoCards(DJCARDS, DJ[iRound]);
	SJCARDS = undoCards(SJCARDS, SJ[iRound]);
}

function modelForward1Round(iRound)
{
	MYCARDS = redoCards(MYCARDS, BJ[iRound]);
	XJCARDS = redoCards(XJCARDS, XJ[iRound]);
	DJCARDS = redoCards(DJCARDS, DJ[iRound]);
	SJCARDS = redoCards(SJCARDS, SJ[iRound]);
}
