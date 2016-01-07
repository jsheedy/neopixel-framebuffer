all:
	browserify -t debowerify src/index.js -o js/app.js

develop:
	beefy src/index.js:js/app.js --live --open

clean:
	rm app.js
