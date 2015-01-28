# Copyright 2015 MongoDB, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import logging

logger = logging.getLogger('giza.content.apiargs.tasks')

from giza.tools.files import expand_tree, safe_create_directory
from giza.content.apiargs.migration import task as migration_task
from giza.content.apiargs.inheritance import ApiArgDataCache
from giza.content.apiargs.views import render_apiargs
from giza.config.content import new_content_type
from giza.tools.timing import Timer
from giza.core.task import Task

def register_apiargs(conf):
    conf.system.content.add(name='apiargs', definition=new_content_type(name='apiargs', task_generator=apiarg_tasks, conf=conf))

def write_apiargs(apiargs, fn):
    content = render_apiargs(apiargs)
    content.write(fn)
    # logger.info('wrote apiarg table to: ' + fn)

def apiarg_tasks(conf):
    with Timer('apiargs migrations'):
        name_changes = migration_task(task='branch', conf=conf)

    apiarg_sources = conf.system.content.apiargs.sources
    a = ApiArgDataCache(apiarg_sources, conf)

    if len(apiarg_sources) > 0 and not os.path.isdir(conf.system.content.apiargs.output_dir):
        safe_create_directory(conf.system.content.apiargs.output_dir)

    tasks = []
    for dep_fn, apiargs in a.file_iter():
        basename = conf.system.content.steps.get_basename(dep_fn)[2:]
        out_fn = os.path.join(conf.system.content.apiargs.output_dir, basename) + '.rst'

        t = Task(job=write_apiargs,
                 args=(apiargs, out_fn),
                 target=out_fn,
                 dependency=dep_fn,
                 description="write apiarg table for: " + dep_fn)
        tasks.append(t)

    logger.info('new apiargs not yet implemented, but there are {0} of them'.format(len(conf.system.content.apiargs.sources)))
    logger.info('added tasks for {0} apiarg table generation tasks'.format(len(tasks)))

    return tasks
