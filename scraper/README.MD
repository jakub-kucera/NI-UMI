This program will find a path between 2 urls.  
The algorithm used is a modified A*.  
The heuristic used: 
* prioritizes pages that have an `.edu` domain
* de-prioritizes pages that are on the same domain as their predecessor
* de-prioritizes pages with a `HTTP` url instead of `HTTPS`
To cut down the number of pages to search, some urls are ignored. Amongst those are:
* invalid URLs
* URLs to files of types such as: PDF, DOCX, ZIP, etc.  

Example of a found path  
1. https://fit.cvut.cz/  
2. https://fit.cvut.cz/cs/zivot-na-fit/aktualne/zpravy/18980-jak-snizit-mnozstvi-plastu-v-oceanech-reseni-nasli-studenti-fit-a-fa  
3. https://euroteq.eurotech-universities.eu/initiatives/competitions/the-euroteq-collider/  
4. https://www.polytechnique.edu/en  
5. https://programmes.polytechnique.edu/en/bachelor/bachelor-of-science  
6. http://web.mit.edu/  
Time taken: 0:01:25.400184

### How to run
1. create a python virtual interface (recommended Python 3.10+)
```shell
python3 -m venv .venv
```
2. activate the virtual interface
```shell
source .venv/bin/activate
```
3. install the requirements
```shell
pip install -r requirements.txt
```
4. show help how to run the program
```shell
python main.py --help
```
