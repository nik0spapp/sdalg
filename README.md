webpage_segmentation
======================
The attached code implements SD algorithm which proceeds to web page segmentation and noise removal
and returns the identified web page type (Article, Article with Comments and Multiple areas) along with
the region annotations per type, which was described in the following paper: 
<ul><li>Nikolaos Pappas, Georgios Katsimpras, Efstathios Stamatatos, <i>Extracting Informative Textual Parts from Web Pages Containing User-Generated Content</i>, 12th Int. Conference on Knowledge Management and Knowledge Technologies, Graz, Austria, 2012 
<br /> <a href="http://publications.idiap.ch/downloads/papers/2012/Pappas_I-KNOW_2012.pdf" target="_blank">http://publications.idiap.ch/downloads/papers/2012/Pappas_I-KNOW_2012.pdf</a>
</li></ul>

Dependencies
------------
The available code for unsupervised sentiment classification requires Python programming 
language and pip package manager to run. For detailed installing instructions please refer to 
the following links: <br />
http://www.python.org/getit/ <br />
http://www.pip-installer.org/en/latest/

After installing them, you should be able to install the following packages: <br />
```bash
$ pip install nltk  
$ pip install urllib 
$ pip install lxml 
```

Examples
--------
To run the SD algorithm simply execute the sd_algorithm.py file and give as parameter 
the URL of your preference. Make sure that you use double quotes in case of weird parameters
on the URL, check examples below. Lastly, the algorithm relies on two thresholds that have
to be tuned on a subset of your target documents (see the related paper), otherwise the 
segmentation may not be as expected. 

```bash
$ python sd_algorithm.py http://www.bbc.co.uk/news/world-africa-12328506
[*] Create DOM tree...
[*] Calculating initial groups...
[*] Merging groups...
[*] Creating regions...
[*] Calculating distances from max region...
[*] Printing regions...

[*] Validating candidate comment group based on its content...

[INFO:] Article detected!
Article class: 
[x] 'story-body'
Article title: 
Egypt protest: 'Carnival atmosphere' among demonstrators
Article text: 
For many in Tahrir Square in central Cairo, the days are starting to take on a familiar pattern. After 
nearly a week of demonstrations, many people now sleep here. There are a few tents and pieces of cardboard 
that serve as beds on a small patch of grass in front of a government building, the Mugamma. "We get just 
four hours sleep or so and then we wake up to start the protest again," said Samah al-Dweik, who has not been 
to her home in Maadi, just outside the city, since Friday.  "We do not know how long we will have to continue. 
Only if Mubarak goes, will we go home. 
(...)
They declare: "I'm free" and "Game over" but also demand policy changes from Western countries that have 
supported the Mubarak government. "US: we hate your hypocrisy" read one banner, referring to the disparity 
between American calls for human rights and democracy and its support of their president. "Listen to the Egyptian 
people," another demanded. Despite an official curfew, the numbers in the square swell in early evening and the 
chants increase in volume. Protesters are only too aware of the government's hope that by delaying its response 
to their demands it will drain their energy.  But they say they are determined to prove otherwise. 

[INFO:] No comments found.
```


```bash
$ python sd_algorithm.py http://www.care2.com/greenliving/chocolate-may-reduce-risk-of-heart-failure.html
[*] Create DOM tree...
[*] Calculating initial groups...
[*] Merging groups...
[*] Creating regions...
[*] Calculating distances from max region...
[*] Printing regions...

[*] Validating candidate comment group based on its content...

[INFO:] Article with comments detected!
[INFO:] Article detected!
Article class: 
[x] 'article_content'
Article title: 
Chocolate May Reduce Risk of Heart Failure
Article text: 
Forget what you’ve heard about death by chocolate.  A new Harvard study shows that chocolate may be good 
for your heart.  Its a great day for chocolate lovers everywhere. Murray Mittleman and his colleagues 
at Harvard Medical School studied data on 31,823 middle-aged and elderly Swedish women to assess the 
relationship between chocolate and heart failure.  The women who consumed an average of one to two servings 
(that’s a fairly small amount) of high-quality, cocoa-rich chocolate per week had a 32 percent lower risk 
of experiencing heart failure. Those women who ate 1 to 3 servings a month had a 26 percent lower risk of 
heart failure. The scientists noted that the high concentration of phytonutrients called flavonoids in 
dark chocolate are potent antioxidants that are likely responsible for the results.  The flavonoids are 
believed to lower blood pressure and reducing inflammation linked with heart failure. Keep in mind that 
not just any chocolate will do.  Forget the vast majority of candy bars on the market.The study results 
were achieved with high-quality, cocoa-rich chocolate.  Read DARK chocolate.  The darker the better.  
And, be sure the one you choose is low in sugar, has no trans or hydrogenated fats, and no artificial 
colors, flavors, or other synthetic ingredients. Related:Easy Greening: Chocolate 101Chocolate: Fact vs. 
FictionDark Chocolate Definitely Eases Emotional StressChocolate Tantric Pie Subscribe to my free 
e-newsletter Worlds Healthiest News for more cutting-edge health news, tips, recipes, and more. 

Comment class:
[x] comment_text contain_floats
Comments:

I love chocolates and I'm very pleased on how nutritious it is. I gained a lot of information about 
chocolates on chocolarious.com and now I'm a certified chocoholic. lol.Also, try checking out 
milkdelight.com, coffeefashion.com, everything-cake.com, and zcocktails.com. =>


The darker the better - so says the author. However, keep in mind that something is better than nothing 
- like the bournvita, cocoa and other drinks. BTW, the article is a reminder to me to have today's 
quota of my chocolate!


I love chocolate. I can go to bed with chocolate in my mouth. Not good for my teeth or weight, but I 
dont have a teeth or weight problem. I guess I'm just lucky. I would have to eat at least 4oz's of 
chocolate a day. Addicted to the great stuff. Thanks for the assurance I'm doing the right thing by 
eating so much of it. :)


Thank you for sharing.
```



```bash
$ python sd_algorithm.py "http://www.lonelyplanet.com/thorntree/forum.jspa;jsessionid=57DA8CB66960A9D820CAB16BB221094D.app01?forumID=34&errorMsg=The%20thread%20requested%20is%20not%20currently%20available"
[*] Create DOM tree...
[*] Calculating initial groups...
[*] Merging groups...
[*] Creating regions...
[*] Calculating distances from max region...
[*] Printing regions...

[INFO:] Multiple similar regions detected!
[x]
Texts: 

Hi All,Am going for a six month trip to Central Asia, Nepal and China.I need to sort our my 
connectivity needs...I will have a mac and a smartphone with me (samsung Note 2, unlocked). I would 
like to find the most convenient way to get on the internet and use the phone locally (no real need 
for voice long distance, and i can always use skype for that).What options do i have considering 
that. - barring nepal - i will not be staying long in any country (2-3 weeks max).The main priority 
is data really... I guess that when i have the ability to downoad data i can always work out my local 
calls through skype...Is it better to buy a local sim card with data/voice capability in every country 
(ie uzbekistan, tajikistan, kyrgyzstan) or should i go for an international sim card (which one?)? Or 
maybe a combination of the two?Ideas gratefully received...With thanks,Str...more »


Hello everybodyMy boyfriend, who is a carpenter and cabinet maker, is going to work for a few months 
to help fix up an old 17th century farmhouse in a rural area of the Hérault, France. There is no 
internet connection for miles, so in order to communicate more effectively we were thinking of buying 
a tablet that holds a SIM card to Skype or internet. When I was there I noticed Bouygues Telecom was 
the main carrier and they have a good deal for a prepaid SIM card.Formule 24/24, la recharge 20€ est 
valable 1 moisPour 20€ rechargés, vous bénéficiez pendant 1 mois :- d'appels et de SMS illimités 24/24+- 
de 250 Mo d'Internet 3G +- de 4€ de crédit de réserve offertThat sorted, we would love some advice on 
the tablet. Could you please recommend any that:
has a Windows operating system (cause that's wha...

Not quite sure this thread belong here, but oh well.Originally from Australia and I am beginning to 
travel the world by van from the 28th march onwards, starting in NZ and AUS.Now I know whats required 
for car registration in Australia, but I have absolutely no idea what I do with registration whilst 
overseas(planning to be overseas for 12+ years).Do you just register in the country you are a citizen? 
Is there a world registration group?Just what do I have to do to keep on the right side of the laws 
around the globe?Thanks for your timeand happy travels.


Does anyone know how easy it is to draw a route on Google Earth and then export it into a SatNav app 
on a mobile phone, to use off-line?I've moved travelled routes from my Garmin GPS device into Google 
Earth before, could probably do it the other way if necessary, I guess (but probably not enough storage 
space for what I'm thinking of). Thinking of getting a phone that has GPS in it (moving into the 21st 
century - haven't actually ever owned a mobile phone yet!).


Flikr is not the only place to display photos nowadaze... Tumblr and Twitter will accept photos 
uploaded directly from your Flikr account...with just one click of the mouse... Although both Tumblr 
and Twitter have photo upload capabilities...Tumblr allows many more ways to display your photos on 
the Net...And Twitter has a media sidebar feature for photos...which can appear as a slide show...
right next to your Tweets...You don't have to use their twitpic feature if you have a Flikr account...
http://vasenka.tumblr.com/


I am looking for a good MS Windows based program that can keep track of places I have visited. I 
would like to be able to view it hopefully by continent, country, states/provinces/regions/etc, cities/
towns/etc. I currently do this on a MS Excel spreadsheet, but would like to be able to use it to view 
maps indicating somehow the locations I have visited, as well as lists.I would also like to add details 
of my trips to each location, including possibly photos.I live in the U.S.A., and am currently working 
on visiting all 50 states (40 of them done, with 2 more to be added this year).That said, I have also 
travelled internationally. To date I have visited 31 countires across 4 continents, and hope to do more 
in the future.Any thoughts? Anything out there that can do something like this?


Hey everyone i recently took up photography as a hobby and a really enjoying it. i'll be leaving on my 
RTW trip in about a month and will be going through parts of europe first then the middle east, asia 
and south and then north america. yet i want to only carry essential gear for my photography yet still 
want to take great shots. I'm using a Sony A57 with a 18-35mm lens, still in the market for a larger 
and better lens yet i want to ask those here who have done travel photography what essential gear should 
i bring and what can i do without.i'll certainly be taking as compact a tripod as i can find yet i'll 
also be taking filters and lens hoods. this gear is already starting to feel bulky in my mind but can 
i afford to do without these items in the least and is there any other ones i should consider. looking 
forward to all replies.


Sorry, not sure which branch to put this under.I wanted to buy something online in a foreign currency. 
I have done this many times whilst abroad but just wanted to check with the company if it was okay. The 
company told me that they only accept £ UK pounds and euros. I wanted to pay in US$. The question is 
-If I pay in US$ for a euro transaction, does my bank send dollars for the equivalent amount and the 
receiving bank does the exchange? Or, does my bank send euros? I am paying the exchange rate charges so 
I assume my bank sends euros. If that is the case then the receiving company gets euros, so I am a bit 
confused why they would say that. It is a European company, the bank is in Europe, I am European, the 
delivery and invoice address is European, so there are no issues with customs/tax.Thanks.


Greetings, travelers!Heading to South Luangwa National Park in Zambia and then making way by bus to 
Kruger in South Africa over a period of weeks.Wondering if anyone reading this has had experience with
putting a sim in a Boostmobile or Sprint HTC Design Evo 4g? Were you able to get it working on data , 
and if so what speeds? Did the wi fi hotspot function work ?If not HTC, did anyone use a usb modem mi 
fi wi fihotspot in South Africa, Botswana, or Zambia?Here's and example of the device I am talking 
about :Huwaei BROADBAND MIFI WIFI RouterOr did you purchase a local data modem stick and which company 
did you use?Thanks

My last few travel cameras have been from the Panasonic TZ series but the last 2 cameras that I've 
had have readily gotten what looks like dirt in the lens. Has anyone else experienced this problem? I 
want to get a new camera to replace the one with dust in the lens (it is now no longer under warrenty 
so can't get it fixed cheaply) and am wondering whether to go for something else this time and what? 
I like the compact high zoom format of the Panasonic TZ series but maybe this is also the reason for 
the problems? Any recommendations? 
Thanks!
``` 


[![githalytics.com alpha](https://cruel-carlota.pagodabox.com/9919a2eb95aaf5a1d91f0c2c6bd7a9a8 "githalytics.com")](http://githalytics.com/nik0spapp/webpage_segmentation)
