from builtins import object

import logging
import posixpath
import kragle as kg
import nbconvert
import cStringIO
import json
import requests
import arrow
import os

from ..repository import KnowledgeRepository

logger = logging.getLogger(__name__)


class ThemisRepository(KnowledgeRepository):
    _registry_keys = ['kragle']

    def init(self):
        pass


    # ------------- Repository actions / state ------------------------------------
    def session_begin(self):
        pass

    def session_end(self):
        pass

    @property
    def revision(self):
        print 'revision'
        return '1'

    def update(self):
        pass

    def set_active_draft(self, path):
        pass

    @property
    def status(self):
        return {'status': 'super'}

    @property
    def status_message(self):
        return self.status['status']

    # -------------- Post retrieval methods --------------------------------------

    def _dir(self, prefix, statuses):
        for i in [i.get('title') for i in kg.themis.NotebookHub().latest()]:
            yield i

    # -------------- Post submission / addition user flow --------------------
    def _add_prepare(self, kp, path, update=False, **kwargs):
        pass

    def _add_cleanup(self, kp, path, update=False, **kwargs):
        pass

    def _submit(self, path):  # Submit a post for review
        pass

    def _accept(self, path):  # Approve a post to publish
        pass

    def _publish(self, path):  # Publish a post for general perusal
        pass

    def _unpublish(self, path):  # Unpublish a post
        pass

    def _remove(self, path, all=False):
        raise NotImplementedError

    def __set_post_status(self, path, status, revision=None):
        pass

    def __get_post_status(self, path, revision=None):
        return self.PostStatus.PUBLISHED

    # ----------- Knowledge Post Data Retrieval/Pushing Methods --------------------

    def _kp_uuid(self, path):
        return None

    def _kp_exists(self, path, revision=None):
        return True

    def _kp_status(self, path, revision=None, detailed=False):
        print '_kp_status'
        return self.PostStatus.PUBLISHED

    def _kp_get_revision(self, path, status=None, enforce_exists=False):
        print '_kp_revision'
        return 0

    def _kp_get_revisions(self, path):
        print '_kp_revisions'
        raise NotImplementedError

    def _kp_read_ref(self, path, reference, revision=None):
        print '_kp_read_ref'
        print "here:",path, reference
        try:
            if reference == "knowledge.md":
                from jinja2 import DictLoader
                from traitlets.config import Config

                c = Config()
                c.ExtractOutputPreprocessor.output_filename_template = 'images/{unique_key}_{cell_index}_{index}{extension}'

                m = nbconvert.MarkdownExporter(config=c,)
                title = path.split('.kp')[0]
                i = [d for d in kg.themis.NotebookHub().search(title) if title in d.get('title')][0]
                r = requests.get(i.get('url'))
                (markdown, resource) =  m.from_file(cStringIO.StringIO(json.dumps(r.json()['notebook']['content'])))
                thumbnail = 0
                if resource.get('outputs', {}):
                    thumbnail = resource.get('outputs', {}).keys()[0]
                for fn, data in resource.get('outputs', {}).iteritems():
                    try:
                        os.makedirs('/data/kb/{}/images'.format(path))
                    except Exception as e:
                        print e
                    with open('/data/kb/{}/{}'.format(path, fn), 'wb') as fout:
                        fout.write(data)
                header = """---
title: "{title}"
authors:
- {author}
tags:
{tags}
created_at: {created}
updated_at: {created}
thumbnail: {thumbnail}
tldr: |
{tldr}
---
""".format(
    title=title,
    author=i.get('owner'),
    tags='\n'.join(['- {}'.format(l) for l in i.get('tags')] or ["- none"]),
    created=arrow.get(i.get('update_date')).format('YYYY-MM-DD'),
    thumbnail=thumbnail,
    tldr='\n'.join(['    {}'.format(l) for l in (i.get('description', '') or '').split('\n')])
)
                return header + markdown
            if 'images' in reference:
                with open('/data/kb/{}/{}'.format(path, reference), 'rb') as fin:
                    return fin.read()

        except Exception as e:
            import traceback
            traceback.print_exc()
            print e
            raise e

    def _kp_dir(self, path, parent=None, revision=None):
        print path, "parent", parent
        
        try:
            return os.listdir('/data/kb/{}/images'.format(path))
        except:
            return []

    def _kp_has_ref(self, path, reference, revision=None):
        print '_kp_has_ref', path, reference
        return True

    def _kp_diff(self, path, head, base):
        raise NotImplementedError

    def _kp_write_ref(self, path, reference, data, uuid=None, revision=None):
        pass

    def _kp_new_revision(self, path, uuid=None):
        return 0
