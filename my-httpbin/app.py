from flask import Flask, render_template, request, jsonify, make_response, \
	redirect, url_for, abort, Response
import base64, json, gzip, zlib
from io import BytesIO
import time, os


def get_method_info():
	response = {'args': {i: j for (i, j) in request.args.items()}}
	response['headers'] = {i: j for (i, j) in request.headers.items()}
	response['origin'] = request.remote_addr
	response['url'] = request.url

	return response

def data_info():
	response = get_method_info()
	response['form'] = dict()
	for i, j in request.form.lists():
		if len(j) > 1:
			response['form'][i] = j
		else:
			response['form'][i] = j[0]
	response['file'] = {}
	for (i, j) in request.files.items():
		m = j.read()
		try:
			file_data = m.decode()
		except:
			file_data = base64.b64encode(m).decode()
			file_data = ''.join(['data:', j.mimetype, ';base64,', file_data])
		response['file'][i] = file_data
	try:
		response['json'] = request.get_json()
	except:
		response['json'] = None
	try:
		response['data'] = request.data.decode()
	except:
		response['data'] = ''.join(['data:application/octet-stream;base64,',
			base64.b64encode(request.data).decode()])
	return response

def get_headers():
	return dict(reqeust.headers.items())

def resource(filename):
	basepath = os.path.dirname(os.path.abspath(__file__))
	file = os.path.join(basepath, filename)
	try:
		with open(file, 'rb') as f:
			data = f.read()
		return data
	except:
		return 'image not found.'

app = Flask(__name__)

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/ip')
def ip():
	origin_ip = request.remote_addr
	return jsonify({
		'origin': origin_ip
	}), 200

@app.route('/user-agent')
def user_agent():
	user_agent = request.headers.get('User-Agent')
	return jsonify({
		'User-Agent': user_agent
	})

@app.route('/headers')
def headers():
	headers = request.headers
	return jsonify({
		i: j for (i, j) in headers.items()
	})

@app.route('/get')
def get_method_response():
	response = get_method_info()
	return jsonify(response)

@app.route('/post', methods=['POST'])
def post():
	response = data_info()
	return jsonify(response)

@app.route('/patch', methods=['PATCH'])
def patch():
	response = data_info()
	return jsonify(response)

@app.route('/PUT', methods=['PUT'])
def put():
	response = data_info()
	return jsonify(response)

@app.route('/delete', methods=['DELETE'])
def delete():
	response = data_info()
	return jsonify(response)

@app.route('/encoding/utf8')
def utf8_encoding():
	return render_template('UTF-8-demo.html')

@app.route('/gzip')
def get_gzip_data():
	response = dict(gzipped=True)
	response['headers'] = {i: j for (i, j) in request.headers.items()}
	response['method'] = request.method
	response['origin'] = request.remote_addr
	resp_buffer = BytesIO()
	resp_data = gzip.GzipFile(mode='wb', fileobj=resp_buffer)
	resp_data.write(json.dumps(response).encode('utf-8'))
	resp_data.close()
	response = make_response(resp_buffer.getvalue())
	response.headers.set('Content-Type', 'application/json')
	response.headers.set('Content-Encoding', 'gzip')
	return response

@app.route('/deflate')
def get_zlib_data():
	response = dict(deflated=True)
	response['headers'] = {i: j for (i, j) in request.headers.items()}
	response['method'] = request.method
	response['origin'] = request.remote_addr
	resp_data = json.dumps(response).encode()
	response = make_response(zlib.compress(resp_data))
	response.headers.set('Content-Type', 'application/json')
	response.headers.set('Content-Encoding', 'deflate')
	return response

@app.route('/status/<int:code>')
def get_status_code(code):
	response = make_response()
	response.status_code = code
	return response

@app.route('/response-headers')
def get_specify_response_headers():
	return 'This is not done now.'

@app.route('/redirect/<int:count>')
def redirect_n_times(count):
	if count != 1:
		return redirect(url_for('.redirect_n_times', count=count-1),)
	else:
		return redirect(url_for('.get_method_response'))

@app.route('/redirect-to')
def redirect_to_specify_url():
	url = request.args.get('url')
	if url is None:
		abort(500)
	return redirect(url)

@app.route('/relative-rediret/<int:count>')
def what_a_realtive_redirect(count):
	return "?????????????"

@app.route('/absolute-redirect/<int:count>')
def what_a_redirect():
	return "?????????????"

@app.route('/cookies')
def get_cookies():
	return jsonify({"cookies": request.cookies})

@app.route('/cookies/set')
def set_cookies():
	response = make_response(redirect(url_for('.get_cookies')))
	for key, value in request.args.items():
		response.set_cookie(key, value)
	return response

@app.route('/cookies/delete')
def delete_cookies():
	response = make_response(redirect(url_for('.get_cookies')))
	for key in request.args.keys():
		response.delete_cookie(key)
	return response

@app.route('/basic-auth/user/passwd')
def basic_auth():
	return Response('Authorized fail.', 401, {
		'WWW-Authenticate': 'Basic realm="Login Required"'
	})

@app.route('/hidden-basic-auth/user/passwd')
def hidden_basic_auth():
	return ''

@app.route('/digest-auth/user/passwd')
def digest_auth():
	return ''

@app.route('/stream/<int:count>')
def get_stream_data(count):
	pass

@app.route('/delay/<int:seconds>')
def delay_response(seconds):
	time.sleep(seconds)
	return jsonify(get_method_info())

@app.route('/drip')
def drip_data():
	pass

@app.route('/range/1024')
def stream_range_data():
	pass

@app.route('/html')
def get_html_page():
	return render_template('sample.html')

@app.route('/robots.txt')
def get_robot_text():
	pass

@app.route('/deny')
def deny_robot():
	pass

@app.route('/cache')
def get_cache():
	if 'If-Modified-Since' in request.headers or \
		'If-None-Match' in request.headers:
		return jsonify(get_method_info()), 304
	return jsonify(get_method_info()), 200

@app.route('/cache/<int:seconds>')
def set_cache_control(seconds):
	response = get_method_info()
	return jsonify(response), 200, {'Cache-Control': 'max-age={}'.format(seconds)}

@app.route('/bytes/<int:n>')
def get_random_bytes(n):
	pass

@app.route('/stream-bytes/<int:n>')
def stream_n_bytes(n):
	pass

@app.route('/links/<int:n>')
def page_links(n):
	return redirect(url_for('.page_link', n=n, number=0))

@app.route('/links/<int:n>/<int:number>')
def page_link(n, number):
	return render_template('links.html', n=n, number=number)


@app.route('/image')
def get_image():
	return Response(resource('templates/Octocat.png'), 200,
		{'Content-Type': 'image/png'})


@app.route('/image/png')
def get_png_image():
	return Response(resource('templates/Octocat.png'), 200,
		{'Content-Type': 'image/png'})

@app.route('/image/jpeg')
def get_jpeg_image():
	return Response(resource('templates/Octocat.jpg'), 200,
		{'Content-Type': 'image/jpeg'})

@app.route('/image/webp')
def get_webp_image():
	return Response(resource('templates/Octocat.webp'), 200,
		{'Content-Type': 'image/webp'})

@app.route('/image/svg')
def get_svg_image():
	return render_template('svg.svg'), 200, {'Content-Type': 'image/svg+xml'}

@app.route('/forms/post')
def get_html_form():
	return render_template('sample-post.html')

@app.route('/xml')
def get_xml():
	return render_template('sample.xml'), 200, {'Content-Type': 'application/xml'}


if __name__ == '__main__':
	app.run(debug=True)


