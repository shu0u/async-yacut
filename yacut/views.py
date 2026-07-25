from flask import flash, redirect, render_template, url_for

from . import app, db
from .forms import FilesForm, URLForm
from .models import URLMap
from .utils import get_unique_short_id
from .yandex_disk import async_upload_files_to_disk, get_download_url_sync


@app.route('/', methods=['GET', 'POST'])
def index_view():
    form = URLForm()
    if form.validate_on_submit():
        custom_id = form.custom_id.data
        if not custom_id:
            custom_id = get_unique_short_id()
        url_map = URLMap(
            original=form.original_link.data,
            short=custom_id,
        )
        db.session.add(url_map)
        db.session.commit()
        flash(
            url_for('redirect_view', short_id=custom_id, _external=True),
            'short_link'
        )
        return render_template('index.html', form=form)
    return render_template('index.html', form=form)


@app.route('/files', methods=['GET', 'POST'])
async def files_view():
    form = FilesForm()
    results = []
    if form.validate_on_submit():
        files = form.files.data
        uploaded = await async_upload_files_to_disk(files)
        for filename, path, download_url in uploaded:
            if not download_url:
                continue
            short_id = get_unique_short_id()
            url_map = URLMap(
                original=path,
                short=short_id,
            )
            db.session.add(url_map)
            db.session.commit()
            short_link = url_for(
                'redirect_view', short_id=short_id, _external=True
            )
            results.append({
                'filename': filename,
                'short_link': short_link,
            })
    return render_template('files.html', form=form, results=results)


@app.route('/<string:short_id>')
def redirect_view(short_id):
    url_map = URLMap.query.filter_by(short=short_id).first_or_404()
    original = url_map.original
    if original.startswith('/Приложения') or original.startswith('/disk'):
        download_url = get_download_url_sync(original)
        if download_url:
            return redirect(download_url)
    return redirect(original)