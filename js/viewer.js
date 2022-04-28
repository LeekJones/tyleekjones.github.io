import {PythonShell} from 'python-shell';

PythonShell.runString(
	'crif_parser.py',
	null,
	function () {
		if(err) throw err;
		console.log('finished');
	}
)