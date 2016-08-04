#!/usr/bin/env python
# Export all playlists from banshee database to m3u

import subprocess
import urlparse
import urllib
import os
import csv
import argparse

def getSQLArgs(string):
	"""Take string of SQL query arguments and return list"""
	# List arguments of SQL query
	args = string[string.find('(')+1:string.rfind(')')]
	#  Use csv reader to escape quotes and commas in string
	return list(csv.reader(args.splitlines(),
		delimiter=',', quotechar='\''))[0]

def inth(string):
	"""Take string and return integer. Handles non-convertables as -1"""
	try:
		rtn = int(float(string))
	except:
		rtn = -1
	finally:
		return rtn

class Playlist:

	def __init__(self, pid, name, order='pos'):
		"""Create playlist with playlist ID, name and ordering"""
		self.id = pid
		self._name = name # Do not change
		self._namefile = ''.join(x for x in name if x.isalnum())
		self.songs = []
		self.order = order

	def addSong(self, song):
		"""Add song object to playlist"""
		self.songs.append(song)

	def purgeDuplicates(self):
		"""Remove duplicates from list"""
		# This method is slightly complicated but preserves orderability
		songDict = {a1['id']: a1 for a1 in self.songs}
		self.songs = [b1 for _,b1 in songDict.items()]
		self.setSorting()

	def setSorting(self, criterion=0):
		"""Sort songs by file paths"""
		if criterion not in [0, 'id','path','pos']: # Criterion valid
			raise KeyError('Invalid sorting criterion.')
		if criterion != 0:
			self.order = criterion
		self.songs.sort(key=lambda x: str(x[self.order]).lower())

	def printList(self):
		"""Return string list of all song files"""
		self.setSorting()
		rtn = ''
		for song in self.songs:
			rtn += song['path'] + '\n'
		return rtn.strip('\n')

class Database:

	def __init__(self, dbfile):
		"""Get database dump from file"""
		if not os.path.isfile(dbfile):
			raise IOError('Database file not found.')
		try:
			# /usr/bin/sqlite3 ~/.config/banshee-1/banshee.db ".dump"
			p = subprocess.Popen(
				['/usr/bin/sqlite3', dbfile, '.dump'],
				stdout = subprocess.PIPE,
				stdin = subprocess.PIPE,
				stderr = subprocess.PIPE,
			)
			self.sql = p.communicate(input='data_to_write')[0]
		except:
			raise IOError
		self.libID = self.getLibID()
		self.playlists = []
		self.songlist = {} # Song id, song file path

	def getLibID(self):
		"""Retrieve library index"""
		for line in  iter(self.sql.splitlines()):
			if ('INSERT INTO "CorePrimarySources"' in line
			and 'MusicLibrarySource-Library' in line):
				args = line[line.find('(')+1:line.rfind(')')].split(',')
				return inth(args[0])
		# If ID not found
		raise AssertionError('Library ID was not found.')

	def getSonglist(self):
		"""Create song directory"""
		for line in iter(self.sql.splitlines()):
			if 'INSERT INTO "CoreTracks"' in line:
				args = getSQLArgs(line)
				if inth(args[0]) != self.libID:
					continue
				# Decode file path
				fpath = urllib.url2pathname(urlparse.urlparse(args[7]).path)
				# If file not found
				if not os.path.isfile(fpath):
					print 'Not found: ' + fpath + ' # ID: ' + args[1]
					continue
				self.songlist[inth(args[1])] = fpath

	def getPlaylists(self):
		"""List all playlist IDs and names"""
		for line in iter(self.sql.splitlines()):
			if 'INSERT INTO "CorePlaylists"' in line:
				args = getSQLArgs(line)
				if inth(args[0]) != self.libID:
					continue
				self.playlists.append(Playlist(inth(args[1]),args[2], 'pos'))
			elif 'INSERT INTO "CoreSmartPlaylists"' in line:
				args = getSQLArgs(line)
				if inth(args[0]) != self.libID:
					continue
				self.playlists.append(Playlist(inth(args[1]),args[2], 'pos'))

	def getPlaylistByName(self, needle):
		"""Return ID for playlist if exists, -1 otherwise"""
		for pl in self.playlists:
			if pl._name == needle:
				return pl.id
		else:
			return -1

	def fillPlaylists(self):
		"""Fill playlists with songs"""
		for line in iter(self.sql.splitlines()):
			if 'INSERT INTO "CorePlaylistEntries"' in line:
				args = getSQLArgs(line)
				for pl in self.playlists:
					if inth(args[1]) == pl.id:
						arg = inth(args[2])
						if arg not in self.songlist:
							continue
						pl.addSong({
							'id': arg,
							'path': self.songlist[arg],
							'pos': inth(args[3]),
							})
			elif 'INSERT INTO "CoreSmartPlaylistEntries"' in line:
				args = getSQLArgs(line)
				for pl in self.playlists:
					if inth(args[1]) == pl.id:
						arg = inth(args[2])
						if arg not in self.songlist:
							continue
						pl.addSong({
							'id': arg,
							'path': self.songlist[arg],
							'pos': 0,
							})

	def purgeDuplicates(self):
		"""Remove duplicate songs in playlists"""
		for pl in self.playlists:
			pl.purgeDuplicates()

	def sortPlaylist(self, criterion, which=-1):
		"""Sort playlist"""
		if criterion not in ['id','path','pos']: # Criterion valid
			raise KeyError('Invalid sorting criterion.')
		for pl in self.playlists:
			if which == pl.id or which == -1:
				pl.setSorting(criterion)

	def clearDir(self, outdir, ext='m3u'):
		"""Clear directory of all files with the extention"""
		if not os.path.isdir(outdir):
			return
		for playlist in os.listdir(outdir):
			if not playlist.endswith(ext):
				continue
			try:
				os.remove(os.path.join(outdir, playlist))
			except Exception as e:
				print "ERROR: Could not remove playlist: " + str(e)

	def export(self, outdir, ext='m3u', postfix='', clearDir=False):
		"""Write playlists to files"""
		if not os.path.isdir(outdir):
			os.makedirs(outdir)
		elif clearDir:
			self.clearDir(outdir, ext)
		for pl in self.playlists:
			# Open playlist to write in assigned location
			plname = os.path.join(outdir, pl._namefile + postfix + '.' + ext)
			with open(plname, 'wt') as fout:
				fout.write(pl.printList())


if __name__ == '__main__':

	# Defaults
	db = '~/.config/banshee-1/banshee.db'
	outdir = '~/playlists/'
	postfix = ''
	ext = 'm3u'
	clearDir = False
	order = False
	keepDuplicates = False

	# Add arguments
	parser = argparse.ArgumentParser(
		description='Export playlists from database')
	parser.add_argument('-db', metavar='DATABASE', default=db,
		help='path to music library (SQL database) (default: \''
		+ db + '\')')
	parser.add_argument('-outdir', metavar='FILEPATH', default=outdir,
		help='target directory in which to place playlists (default: \''
		+ outdir + '\')')
	parser.add_argument('-postfix', metavar='POSTFIX', default=postfix,
		help='append custom postfix to all playlist names (default: \'\')')
	parser.add_argument('-ext', metavar='EXTENSION', default=ext,
		help='playlist file extension (default: \'m3u\')')
	parser.add_argument('-clearDir', default=clearDir, action="store_true",
		help='clear target directory before inserting playlists')
	parser.add_argument('-keepDuplicates', default=keepDuplicates,
		action="store_true",
		help='keep duplicate song in playlists')
	parser.add_argument('-order', default=order, choices=['pos', 'id', 'path'],
		help='sort playlists by \'order\'. Leave out to disable sorting')
	args = parser.parse_args()

 	# Contruct database
	try:
		bansheeLibrary = Database(os.path.expanduser(args.db))
	except Exception as e:
		print 'ERROR: ' + str(e)
		exit(1)

	bansheeLibrary.getSonglist() # Get list of songs
	bansheeLibrary.getPlaylists() # Get list of playlist IDs and names
	bansheeLibrary.fillPlaylists() # Get playlists' contents

	# Purge duplicate songs in playlists
	if not args.keepDuplicates:
		bansheeLibrary.purgeDuplicates()

	# Sort playlist
	if args.order:
		bansheeLibrary.sortPlaylist(args.order)

	# Store the playlists
	bansheeLibrary.export(
		os.path.expanduser(os.path.normpath(args.outdir)), args.ext,
		args.postfix, args.clearDir)

	exit()
