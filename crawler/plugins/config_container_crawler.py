from plugins.config_crawler import crawl_config_files
from icrawl_plugin import IContainerCrawler
import dockerutils
from namespace import run_as_another_namespace
import misc
import logging

logger = logging.getLogger('crawlutils')


class ConfigContainerCrawler(IContainerCrawler):

    def get_feature(self):
        return 'config'

    def crawl(self, container_id=None, avoid_setns=False,
              root_dir='/', exclude_dirs=[], known_config_files=[],
              discover_config_files=False, **kwargs):
        inspect = dockerutils.exec_dockerinspect(container_id)
        state = inspect['State']
        pid = str(state['Pid'])
        logger.debug('Crawling config for container %s' % container_id)

        if avoid_setns:
            rootfs_dir = dockerutils.get_docker_container_rootfs_path(
                container_id)
            exclude_dirs = [misc.join_abs_paths(rootfs_dir, d)
                            for d in exclude_dirs]
            return crawl_config_files(
                root_dir=misc.join_abs_paths(rootfs_dir, root_dir),
                exclude_dirs=exclude_dirs,
                root_dir_alias=root_dir,
                known_config_files=known_config_files,
                discover_config_files=discover_config_files)
        else:  # in all other cases, including wrong mode set
            return run_as_another_namespace(pid,
                                            ['mnt'],
                                            crawl_config_files,
                                            root_dir,
                                            exclude_dirs,
                                            None,
                                            known_config_files,
                                            discover_config_files)
