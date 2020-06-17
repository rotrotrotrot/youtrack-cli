function _you_completion() {
	you_aliases=`you aliases`
	_arguments ":command:(${you_aliases})"
}

compdef _you_completion `which you`
