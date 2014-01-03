/*!
@author KOLANICH
@license Unlicense

Originally developed in 2013 by KOLANICH

This library is used for solving 'table-type' problems such as
http://mmmf.msu.ru/archive/20052006/z5/11.html


for example

The three clown: Bim, Bom and Bam act in green, red and blue shirts.
Their shoes are the same colors. Colors of Bim's shoes and shirt match.
Neither Bom's shirt, nor shoes are red.
Bam wears green shoes and a shirt of a different color.
What are the colours of their shirts and shoes? (All clowns wear different shirts and different shoes)


var a=new SolutionTable();
var shoes={},shirts={};
a.onResolved.push(console.info);
a.onResolved.push(function(v){for(let n in v)shoes[n]=v[n];});
a.init(["Bim","Bom","Bam"],["r","g","b"]);
a.isNot("Bom","r");//Neither Bom's shirt, nor **shoes are red**.
a.equal("Bam","g");//Bam wears green shoes
a.onResolved[a.onResolved.length-1]=(function(v){for(let n in v)shirts[n]=v[n];});
a.init(["Bim","Bom","Bam"],["r","g","b"]);
a.isNot("Bom","r");//**Neither Bom's shirt**, nor shoes **are red**.
a.isNot("Bam","g");//Bam wears green shoes
a.equal("Bim",shoes["Bim"]);//Colors of Bim's shoes and shirt match.
console.log(shoes,shirts);


One plant employs three friends: turner, fitter and welder. Their surnames are Borisov, Ivanov and Semenov.
The fitter has neither brothers, nor sisters. He is the youngest of the friends.
Semenov is married to Borisov's sister and he is older than the turner. Match the surnames to the occupations.

var a=new SolutionTable();
a.onResolved.push(console.info);
a.init(["turner", "fitter", "welder"],["Borisov", "Ivanov", "Semenov"]);
a.isNot("fitter","Borisov");
a.isNot("turner","Semenov");
a.isNot("fitter","Semenov");
console.log(a.hash1,a.hash2);


This library was initially written for analyzing mafia game.

var a=new SolutionTable();
a.onResolved.push(console.info);
a.init(["maniac","maf","doc","psy"],["pasha","vova","dima","petya"]);
var alone =a.equal("doc","pasha");//we know he is doc
var alone =a.equal("maniac","pasha");//you need to be careful - no checks are implemented, so this will delete maniac column though pasha cannot be a maniac and this can be seen from the table.
console.log(alone,a.hash1,a.hash2);

a.init(["maniac","maf","doc","psy"],["pasha","vova","dima","petya"]);
var alone =a.isNot("doc","pasha");
var alone =a.isNot("maniac","pasha");
var alone =a.isNot("maniac","vova");
var alone =a.isNot("psy","vova");
var alone =a.isNot("psy","dima");
var alone =a.isNot("maniac","dima");
console.log(alone,a.hash1,a.hash2);

*/

function SolutionTable() { //!<@constructor
	this.hash1 = {};
	this.hash2 = {};
	this.onResolved = [];
}

(function(){

/*!
@param src array such as ["a","b","c"] or object as {a:"blahblah",b:2.5,c:/olololshenki/ig}
@returns hash with names as {a:{},b:{},c:{}}
 */
SolutionTable.prototype.unifyToHash = function (src) {
	var hash = {};
	if (src instanceof Array)
		for (var j = 0; j < src.length; j++)
			hash[src[j]] = {};
	else
		for (var j in src)
			hash[j] = {};
	return hash;
}

/*!
@param names1 array or hash of names for category 1
@param names2 array or hash of names for category 2
 */

SolutionTable.prototype.init = function (names1, names2) {
	this.hash1 = this.unifyToHash(names1);
	this.hash2 = this.unifyToHash(names2);
	for (var i in this.hash1) {
		for (var j in this.hash2) {
			this.hash1[i][j] = true;
			this.hash2[j][i] = true;
		}
	}
}

/*!
removes pair <name1> <name2> from both hashtables and resolves
@param name1 - name to remove from set 1
@param name2 - name to remove from set 2
@returns hash {"name1_1":"name2_1","name1_2":"name2_2"}
 */

SolutionTable.prototype.equal=SolutionTable.prototype.removePairAndResolve = function (name1, name2) {
	var res = this.___removePairAndResolve(name1, name2);
	res[name1] = name2;
	this.__triggerOnResolved(res);
	return res;
};

SolutionTable.prototype.__triggerOnResolved = function (resolved) {//<used to trigger needed functions
	if(resolved&&!isEmpty(resolved))this.onResolved.forEach((cb) => cb(resolved, this));
};

SolutionTable.prototype.___removePairAndResolve = function (name1, name2) {
	//console.info("removing pair",name1,":",name2);
	var alone1,
	alone2;
	delete this.hash1[name1];
	delete this.hash2[name2];
	return this.__removeAndResolve(name1, name2);
};

SolutionTable.prototype.isNot = function (name1, name2) {
	//console.info(name1,"is not",name2);
	var alone1, alone2;
	removeItemFromHashTable(this.hash1, name1, name2);
	removeItemFromHashTable(this.hash2, name2, name1);
	//looking for alones
	alone1 = removeFromCandidatesOrLookForAlone(this.hash1);
	alone2 = removeFromCandidatesOrLookForAlone(this.hash2);
	var res = this.__resolve(combineAloneReverse(alone1, alone2));
	this.__triggerOnResolved(res);
	return res;
};

SolutionTable.prototype.__removeAndResolve = function (name1, name2) {
	var alone1, alone2;
	alone2 = removeFromCandidatesOrLookForAlone(this.hash2, [name1]);
	alone1 = removeFromCandidatesOrLookForAlone(this.hash1, [name2]);
	var aloneUnited = combineAloneReverse(alone1, alone2);
	//console.log(aloneUnited);
	return this.__resolve(aloneUnited);
};

SolutionTable.prototype.__resolve = function (alone) {
	//console.info("resolving",JSON.stringify(alone));
	var newAlone = {};
	for (var key in alone) {
		//console.log(key,alone[key],newAlone);
		newAlone = combineAlone(newAlone, this.___removePairAndResolve(key, alone[key]));
	}
	var res = combineAlone(newAlone, alone);
	return res;
};

function combineAlone(alone1, alone2) {
	var aloneUnited = alone1;
	/*var aloneUnited = {};
	for (var a in alone1) {
	aloneUnited[a] = alone1[a];
	}*/
	for (var a in alone2) {
		aloneUnited[a] = alone2[a];
	}
	return aloneUnited;
};

function combineAloneReverse(alone1, alone2) {
	var aloneUnited = alone1;
	/*var aloneUnited = {};
	for (var a in alone1) {
	aloneUnited[a] = alone1[a];
	}*/
	for (var a in alone2) {
		aloneUnited[alone2[a]] = a;
	}
	return aloneUnited;
};

SolutionTable.prototype.add = function (name1, name2, val) {
	val = val || true;
	if (!this.hash1[name1])
		this.hash1[name1] = {};
	if (!this.hash2[name2])
		this.hash2[name2] = {};
	this.hash1[name1][name2] = val;
	this.hash2[name2][name1] = val;
};

function countItemsInHashtable(hashTable) {
	var count = 0, el;
	for (el in hashTable) {
		count++;
	}
	return count;
};

function onlyElKeyInHashtable(hashTable) { //!<returns the key of the only element in hashtable
	var count = 0, el;
	for (el in hashTable) {
		count++;
	}
	return (count == 1 ? el : null);
};

/*!
looks for alone or removes from candidates
@param hashtable - hashtable of hashtables
outer hashtable's keys are categories
inner hashtable's keys are candidates
@param known - array of names of known
@returns hash {category:alone}
 */
function removeFromCandidatesOrLookForAlone(hashTable, known) {
	//console.info("removing from candidates or looking for alone");
	var alone = {}, aloneItem = null;
	known = known || [];
	for (var unknown in hashTable) {
		for (var i = 0; i < known.length; i++) {
			if (hashTable[unknown][known[i]]) {
				removeItemFromHashTable(hashTable, unknown, known[i]);
			}
		}
		if (aloneItem = onlyElKeyInHashtable(hashTable[unknown])) {
			alone[unknown] = aloneItem;
		}
	}
	return alone;
};

function removeItemFromHashTable(hashTable, name1, name2) { //!removes item from hashtable
	//hashTable[name1][name1]=null;
	if (!hashTable[name1])
		return false;
	delete hashTable[name1][name2];
	if (countItemsInHashtable(hashTable[name1]) == 0)
		delete hashTable[name1];
};

function isEmpty(obj) {
	for (var a in obj)
		return 0;
	return 1;
};

})();
