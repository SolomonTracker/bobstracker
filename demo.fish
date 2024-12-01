source venv/bin/activate.fish
cd demo
rm pkg_*.png
alias generate "python ../execute.py generate"
alias newpackage "python ../execute.py newpackage"
alias package "python ../execute.py package"
alias clean "python ../execute.py clean"
alias showdiff "python ../execute.py showdiff"
alias toyexample "python ../execute.py toyexample"
alias graph "xdg-open .graph.gv.pdf"
