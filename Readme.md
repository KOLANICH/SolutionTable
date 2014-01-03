SolutionTable.js
=================
This library was initially written for analyzing mafia games but it is suitable to solving problems.
it has 3 main methods:
.init([one set],[another set]) - initializes table columns and rows
.aIsNotB("element of the first set","element of the second set") - used when it is known that 2 elements differ
.removePairAndResolve(name1, name2) - used when it is known that 2 elements are equal

Look the examples (the problems were taken from http://mmmf.msu.ru/archive/20052006/z5/11.html) .

Problem 1
---------
The three clown: Bim, Bom and Bam act in green, red and blue shirts.
Their shoes are the same colors. Colors of Bim's shoes and shirt match.
Neither Bom's shirt, nor shoes are red.
Bam wears green shoes and a shirt of a different color.
Dressed as clowns? (All clowns wear different shirts and different shoes)

```js
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
```

Problem 2
---------

One plant employs three friends: turner, fitter and welder. Their surnames are Borisov, Ivanov and Semenov.
The fitter has neither brothers, nor sisters. He is the youngest of the friends.
Semenov is married to Borisov's sister and he is older than the turner. Match the surnames to the occupations.
```js
var a=new SolutionTable();
a.onResolved.push(console.info);
a.init(["turner", "fitter", "welder"],["Borisov", "Ivanov", "Semenov"]);
a.isNot("fitter","Borisov");
a.isNot("turner","Semenov");
a.isNot("fitter","Semenov");
console.log(a.hash1,a.hash2);
```

[Mafia Game](https://en.wikipedia.org/wiki/Mafia_%28party_game%29)
------------------------------------------------------------------
Initially this was developed to unreveal roles from mafia game log
```js
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
```
Apache Liscense
------------

    Copyright 2013 KOLANICH
    
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at
    
    http://www.apache.org/licenses/LICENSE-2.0
    
    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.