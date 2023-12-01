#! /usr/bin/env python3

import sys
from argparse import ArgumentParser
from pathlib import Path
import json
from textwrap import dedent

import plistlib
from typing import Optional, List, Dict

# title of the reading list array in the XML/Dict
READING_LIST_TITLE = 'com.apple.ReadingList'

BOOKMARKS_PATH_DEFAULT = Path('~/Library/Safari/Bookmarks.plist').expanduser().as_posix()

def load_plist_file(file_path: str) -> dict:
	with open(file_path, 'rb') as f:
		d = plistlib.load(f, fmt=plistlib.FMT_BINARY)

	return d


def get_reading_list_data(data: dict) -> Optional[dict]:
	"""Extract the reading list data from the full bookmarks data

	Will return None if not found

	Will raise ValueError if more than one found
	"""

	# get the reading list data out of the full bookmarks data
	# can only identify by finding a dictionary that has the reading list title (cons above)
	#    as the value for the "Title" key
	reading_list_index = []
	for i, b in enumerate(data['Children']):
		if b.get('Title') == READING_LIST_TITLE:
			reading_list_index.append(i)

	# If none found ... None
	if not reading_list_index:
		return None

	# if more than one found ... error
	if len(reading_list_index) > 1:
		raise ValueError(
			'data has more than one ({}) element with title "{}"'.format(
				len(reading_list_index),
				READING_LIST_TITLE
				)
			)

	else:
		index = reading_list_index[0]
		return data['Children'][index]


def make_url_preview_datetime_list_of_reading_list(
			reading_list_data: dict
		) -> List[ Dict[str, Optional[str]] ]:
	"""Generate flat list of each reading list item as a dict with relevant data

	For each reading list item create dict of following structure:

		{
			'url': str,
			'preview': str | None,
			'title': str | None,
			'date_added': date_added_str | None
		}
	"""

	reading_list_items: list = reading_list_data['Children']

	# check no folders and all have URLs

	has_title = ['Title' in i for i in reading_list_items]  # a title is typically for a container
	has_url = ['URLString' in i for i in reading_list_items]  # not a bookmark unless has URL!

	if any(has_title):
		print(
			'WARNING: Some reading list items seem to be not bookmarks but containers (n = {})'
			.format(sum(has_title))
			)
	if not all(has_url):
		print(
			'WARNING: Some reading list items do not have URLs (n = {})'
			.format(sum(has_url))
			)

	new_rl_data = []
	for i, rl_item in enumerate(reading_list_items):
		# passing over a lack of URL silently!!! Oooof!  Still, of no URL, who cares ... ?
		if has_url[i]:
			preview = None
			date_added_str = None
			title = None

			# Dict with core data
			item_data = rl_item.get('ReadingList')

			if item_data:

				date_added = item_data.get('DateAdded')
				if date_added:
					date_added_str = date_added.strftime('%Y-%m-%d')

				preview = item_data.get('PreviewText')

			# Dict with local data
			non_sync_data = rl_item.get('ReadingListNonSync')
			if non_sync_data:
				title = non_sync_data.get('Title')

			new_rl_item = {
				'url': rl_item.get('URLString'),
				'preview': preview,
				'title': title,
				'date_added': date_added_str
			}

			new_rl_data.append(new_rl_item)

	return new_rl_data


if __name__ == '__main__':

	parser = ArgumentParser(description='Convert bookmarked reading list data')

	parser.add_argument(
			'-f', '--file',
			help='location of the bookmarks file',
			default=BOOKMARKS_PATH_DEFAULT
		)

	FORMAT_OPTIONS = ('JSON', 'plain')
	parser.add_argument(
			'--format',
			help=f'Format of output {FORMAT_OPTIONS}',
			choices=FORMAT_OPTIONS,
			default='JSON'
		)

	SORT_OPTIONS = {'title': 'title', 'date': 'date_added'}
	parser.add_argument(
			'--sort',
			help='Whether to sort and if so by what value (title, date) (default is no sort)',
			choices=SORT_OPTIONS.keys(),
			default = None
		)

	parser.add_argument(
			'--reverse',
			help='If sorting, will sort in reverse',
			action='store_true'
		)

	args = parser.parse_args()

	rl_data = get_reading_list_data(load_plist_file(args.file))

	if rl_data is not None:
		new_rl_data = make_url_preview_datetime_list_of_reading_list(rl_data)
	else:
		print(f'Failed to find reading list data in bookmarks (key: {READING_LIST_TITLE})')
		sys.exit()

	if args.sort:
		# check sort value actually available (could enforce in argparse, but maybe this is more flexible?)
		sort_value = SORT_OPTIONS[args.sort]
		if not sort_value in new_rl_data[0]:
			print(f'Sort value not found in data ({sort_value})', file=sys.stderr)
			sys.exit()

		new_rl_data = sorted(
					new_rl_data,
					key = lambda x: x.get(sort_value) or '',
					reverse = args.reverse
				)

	if args.format == 'JSON':
		try:
			json_data = json.dumps(new_rl_data)
		except Exception as e:
			print('Failed to convert data to JSON',file=sys.stderr)
			print('Exception trace:\n-------------\n\n', file=sys.stderr)
			raise e
		print(json_data)

	if args.format == 'plain':
		try:
			string_data = (
				dedent(
						f'''
						* {t['title']}
						* {t['preview']}
						* {t['date_added']}
						* {t['url']}
						'''
					)
				for t in new_rl_data
			)
		except Exception as e:
			print('Failed to convert data to string', file=sys.stderr)
			raise e

		full_string = '\n---\n'.join(string_data)
		print(full_string)

