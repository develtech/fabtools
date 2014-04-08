#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import with_statement

import posixpath as path

from fabric.api import task


REMOTE_URL = 'lp:bzr-hello'
DIR = REMOTE_URL.split(':')[1]


@task
def bazaar():
    """
    Test some low level bazaar tools.
    """

    from fabric.api import cd, sudo

    with cd('/tmp'):
        # Clean up
        sudo('rm -rf *')

        bzr_wc_source_remote()
        bzr_wc_source_local()
        bzr_wc_default_target()
        bzr_wc_version()
        bzr_wc_target_exists_no_update()
        bzr_wc_target_exists_update()
        bzr_wc_target_exists_version()
        bzr_wc_target_exists_local_mods_no_force()
        bzr_wc_target_exists_local_mods_force()
        bzr_wc_sudo()
        bzr_wc_sudo_user()

def assert_wc_exists(wt):
    from fabtools.files import is_dir

    assert is_dir(wt)
    assert is_dir(path.join(wt, '.bzr'))
    assert is_dir(path.join(wt, '.bzr', 'checkout'))

def bzr_wc_source_remote():
    """
    Test creating working copy from a remote source.
    """

    from fabtools.files import is_dir
    from fabtools import require

    wt = DIR + '-test-wc_source_remote'

    assert not is_dir(wt)

    require.bazaar.working_copy(REMOTE_URL, wt)

    assert_wc_exists(wt)

def bzr_wc_source_local():
    """
    Test creating working copy from a local source.

    Note: this requires bzr to be installed on local host, if bzr is not
    available, this test is skipped with a warning.
    """

    from fabric.api import local, puts, settings

    with settings(warn_only=True):
        bzr = local('which bzr', capture=True)

    if bzr.failed:
        puts('wc_source_local: SKIP: Bazaar not installed on local host')
        return

    from fabtools import require

    wt = DIR + '-test-wc_source_local'
    local('test ! -e %(wt)s || rm -rf %(wt)s' % {'wt': wt})
    local('bzr branch %s %s' % (REMOTE_URL, wt))

    assert not is_dir(wt)

    require.bazaar.working_copy(wt, wt)

    assert_wc_exists(wt)

    local('rm -rf %s' % wt)

def bzr_wc_default_target():
    """
    Test creating a working copy at a default target location.
    """

    from fabtools.files import is_dir
    from fabtools import require

    assert not is_dir(DIR)

    require.bazaar.working_copy(REMOTE_URL)

    assert_wc_exists(DIR)

def bzr_wc_version():
    """
    Test creating a working copy at a specified revision.
    """

    from fabric.api import run

    from fabtools.files import is_dir
    from fabtools import require

    wt = DIR + '-test-wc_version'

    assert not is_dir(wt)

    require.bazaar.working_copy(REMOTE_URL, wt, version='2')

    assert_wc_exists(wt)
    assert run('bzr revno %s' % wt) == '2'

def bzr_wc_target_exists_no_update():
    """
    Test creating a working copy when target already exists and updating was
    not requested.
    """

    from fabtools.files import is_dir
    from fabtools import require

    wt = DIR + '-test-wc_target_exists_no_update'

    assert not is_dir(wt)
    run('mkdir %s' % wt)

    require.bazaar.working_copy(REMOTE_URL, wt, update=False)

    assert not is_dir(path.join(wt, '.bzr'))

def bzr_wc_target_exists_update():
    """
    Test creating/updating a working copy when a target already exists.
    """

    from fabric.api import run

    from fabtools.files import is_dir
    from fabtools import require

    wt = DIR + '-test-wc_target_exists_update'

    assert not is_dir(wt)

    require.bazaar.working_copy(REMOTE_URL, wt, version='2')

    require.bazaar.working_copy(REMOTE_URL, wt, update=True)

    assert_wc_exists(wt)
    assert int(run('bzr revno %s' % wt)) > 2

def bzr_wc_target_exists_version():
    """
    Test updating a working copy when a target already exists.
    """

    from fabric.api import run

    from fabtools.files import is_dir
    from fabtools import require

    wt = DIR + '-test-wc_target_exists_update'

    assert not is_dir(wt)

    require.bazaar.working_copy(REMOTE_URL, wt, version='2')

    require.bazaar.working_copy(REMOTE_URL, wt, version='4', update=True)

    assert_wc_exists(wt)
    assert run('bzr revno %s' % wt) == '4'

def bzr_wc_target_exists_local_mods_no_force():
    """
    Test working copy when a target already exists and has local modifications
    but force was not specified.
    """

    from fabric.api import cd, run

    from fabtools.files import is_dir
    from fabtools import require

    wt = DIR + '-test-wc_target_exists_local_mods_no_force'
    require.bazaar.working_copy(REMOTE_URL, wt)

    assert is_dir(wt)

    with cd(wt):
        assert run('bzr status') == ''

        run('echo "# a new comment" >> __init__.py')

        assert run('bzr status') != ''

    try:
        require.bazaar.working_copy(REMOTE_URL, wt)
    except SystemExit:
        pass
    else:
        assert False, "working_copy didn't raise exception"

def bzr_wc_target_exists_local_mods_force():
    """
    Test working copy when a target already exists and has local modifications
    and force was specified.
    """

    from fabric.api import cd, run

    from fabtools.files import is_dir
    from fabtools import require

    wt = DIR + '-test-wc_target_exists_local_mods_force'
    require.bazaar.working_copy(REMOTE_URL, wt)

    assert is_dir(wt)

    with cd(wt):
        assert run('bzr status') == ''

        run('echo "# a new comment" >> __init__.py')

        assert run('bzr status') != ''

    require.bazaar.working_copy(REMOTE_URL, wt, force=True)

    assert run('bzr status %s' % wt) == ''

def bzr_wc_sudo():
    """
    Test working copy with sudo.
    """

    from fabric.api import sudo

    from fabtools.files import group, is_dir, owner
    from fabtools import require

    assert not is_dir(wt)

    wt = DIR + '-test-wc_sudo'
    require.bazaar.working_copy(REMOTE_URL, wt, use_sudo=True)

    assert_wc_exists(wt)
    assert owner(wt) == 'root'
    assert group(wt) == 'root'

def bzr_wc_sudo_user():
    """
    Test working copy with sudo as a user.
    """

    from fabric.api import cd, sudo

    from fabtools.files import group, is_dir, owner
    from fabtools import require

    require.user('bzruser', group='bzrgroup')

    assert not is_dir(wt)

    wt = DIR + '-test-wc_sudo_user'
    require.bazaar.working_copy(REMOTE_URL, wt, use_sudo=True, user='bzruser')

    assert_wc_exists(wt)
    assert owner(wt) == 'bzruser'
    assert group(wt) == 'bzrgroup'
