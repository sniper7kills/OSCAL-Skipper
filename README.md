== OSCAL Skipper Project Generation Script ==
The following script was created in order to generate a Skipper18 Project based on the OSCAL metaschema.

'start.py is the entry point; and will use the oscal and skipper files to process
their data respectively.

To Use:
```
cd oscal-python
chmod +x start.py
python3 ./start.py > output-results.skipper
```
Then open "output-results.skipper" in Skipper18

Download and Store the "oscal_complete_schema.json" file and store it one directory above where this file is located.
/root
/root/oscal_complete_schema.json
/root/oscal-python/start.py
/root/oscal-python/oscal.py
/root/oscal-python/skipper.py

To anyone reading this code in the future;
And espically to anyone that needs to maintain this in the future....

I am truly sorry for the lack of documentation.
This is V5 during development, and is much better than V1 was...
But that is no excuse. All code should be readable, and documented.

I could get hit by a bus tomorrow, and someone else will need to maintain this.
I truly hope they (you) will forgive me, and that the Code Gods will have mercy on my source code.

(c) 6 NOV 2021 - Will G // Sniper7Kills LLC
