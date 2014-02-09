// this file may differ on different platforms. They are all about UI displaying.
function displayGameEnd()
{
	alert("end");
}

function displayRoundCore(iRound, bottom, bottomarr, right, rightarr, up, uparr, left, leftarr, bottomCARDS, rightCARDS, upCARDS, leftCARDS)
{

	document.getElementById("ZHUJIPAI").innerText="Ö÷ÅÆ:"+ZHUJIPAI;


	if (iRound == -1)
	{
		document.getElementById("BJ").innerText=bottom;
		document.getElementById("DJ").innerText=up;
		document.getElementById("SJ").innerText=left;
		document.getElementById("XJ").innerText=right;
		document.getElementById("ROUNDCOUNT").innerText="READY? GO!";
		document.getElementById("MYCARDS").innerText=prettyFormat2(bottomCARDS);
		document.getElementById("DJCARDS").innerText=prettyFormat2(upCARDS);
		document.getElementById("SJCARDS").innerText=prettyFormat2(leftCARDS);
		document.getElementById("XJCARDS").innerText=prettyFormat2(rightCARDS);
		return true;
	}

	document.getElementById("ROUNDCOUNT").innerText="µÚ" + (iRound+1) + "ÂÖ";
	document.getElementById("BJ").innerText=bottom+":"+prettyFormat(bottomarr[iRound]);
	document.getElementById("DJ").innerText=up+":"+prettyFormat(uparr[iRound]);
	document.getElementById("SJ").innerText=left+":"+prettyFormat(leftarr[iRound]);
	document.getElementById("XJ").innerText=right+":"+prettyFormat(rightarr[iRound]);

	if (strEq(SXD[iRound], bottom)){document.getElementById("BJ").innerText = "### "+document.getElementById("BJ").innerText}
	if (strEq(SXD[iRound], right)){document.getElementById("XJ").innerText = "### "+document.getElementById("XJ").innerText}
	if (strEq(SXD[iRound], up)){document.getElementById("DJ").innerText = "### "+document.getElementById("DJ").innerText}
	if (strEq(SXD[iRound], left)){document.getElementById("SJ").innerText = "### "+document.getElementById("SJ").innerText}

	document.getElementById("MYCARDS").innerText=prettyFormat2(bottomCARDS);
	document.getElementById("DJCARDS").innerText=prettyFormat2(upCARDS);
	document.getElementById("SJCARDS").innerText=prettyFormat2(leftCARDS);
	document.getElementById("XJCARDS").innerText=prettyFormat2(rightCARDS);

	return true;
}
