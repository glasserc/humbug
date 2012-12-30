Humbug is a program to manage your `git-annex
<http://git-annex.branchable.com/>`_\ 'd Humble Indie Bundle files as
more Bundles are released and the old ones updated.

It relies on the property that when a file is updated on the Humble
Bundle site, its filename changes, usually in a predictable way (a
version number increases). If the filename on the Humble Bundle site
exists locally, we don't need to download it again.

Of course, not all filename changes indicate version
changes. Sometimes the people at Humble Bundle, Inc. just like to
change filenames to see if we're paying attention. Other times they
introduce a new version of a file and change the old file's name to
clarify things -- for example, they may introduce a new FLAC
soundtrack and rename the old soundtrack to make it clear that it is
the MP3 version.

Humbug can help you keep a local copy of your Humble Bundle
collection. It compares the links in a Humble Bundle home page to the
files in your git annex and tries to determine:

1. which files are missing and need to be added to the local
   copy. These files need to be downloaded, and then added using ``git
   annex add``.
2. which files are present in the local copy, but have been
   renamed. These files can be renamed using ``git mv``.
3. which files that are present in the local copy are actually older
   versions of things that have been updated in the Humble Bundle
   collection. Newer versions can be downloaded (as per 1) and then
   the old versions can be removed using ``git annex drop -f`` and
   ``git rm``.

This program is very much designed to scratch my own personal
itch. You might be more interested in `humblepie
<https://github.com/zendeavor/humblepie/blob/master/humblepie>`_ or
`t4b's HIB script
<http://t4b.me/posts/downloading-all-your-hib-games/>`_.


Dependencies
------------

- BeautifulSoup4 (packaged sometimes as python-bs4)
- Python 2.7 (because we use OrderedDict)
- snarf (small program similar to wget with a nicer command-line arguments)
- atools (for aunpack, which you probably want to install anyhow --
  just trust me)

Usage
-----

First, go to the `Humble Bundle home page
<https://www.humblebundle.com/home>`_ and sign in. You might have to
click "My Account". Are you at that page showing all your games?
Good. In your browser, save this page (File->Save). Make note of where
you saved this file, and what you called it (by default, Firefox will
give it the name home.html). The links in this page "expire" so be
sure to refresh if you're already there.

``cd`` to the repo containing your annex. Run::

    $ python ~/path-to-humbug/humbug.py ~/path-to-home-html/home.html

Humbug will take a few seconds to parse the enormous mass of HTML,
CSS, and JavaScript that you saved and will compare it to what it sees
on your disk. Finally, it will print out a report like this::

    Can't download non-file 'Stream' (for 'Indie Game - The Movie')
    Can't download non-file 'Stream' (for 'Kooky')
    Can't download non-file 'Read Me' (for 'Signal to Noise')
    Can't download non-file 'Coming Shortly' (for 'Vessel')
    Can't download non-file 'Soundtrack website' (for 'World of Goo')
    Leftover files: [u'crayon-physics-deluxe_55_i386.rpm']
    Problems were found with these downloads:
      Problem: couldn't verify that Swords_and_Soldiers_soundtrack_mp3.zip was swords_and_soldiers-ost-mp3.zip ("git annex get" and retry)
      Problem: couldn't verify that swordsandsoldiers_20120325-1_amd64.deb was swordsandsoldiers-linux-20120325-ubuntu-amd64.deb ("git annex get" and retry)
      Problem: couldn't verify that MachinariumSoundtrack.zip was machinarium-ost-mp3.zip ("git annex get" and retry)
        - Download machinarium-ost-flac.zip to Games/Machinarium/Soundtrack/machinarium-ost-flac.zip (other problems in this directory)
      Problem: couldn't verify that swordsandsoldiers_20120325-1_i386.deb was swordsandsoldiers-linux-20120325-ubuntu-i386.deb ("git annex get" and retry)
      Problem: couldn't verify that crayon-physics-deluxe_55_i386.deb was crayon_physics_deluxe-1.0.55-ubuntu-i386.deb ("git annex get" and retry)
      Problem: couldn't verify that crayon-physics-deluxe_55_i386.tar.gz was crayon_physics_deluxe-linux-release55.tar.gz ("git annex get" and retry)
      Problem: couldn't figure out uplink_1.6-1_i386.deb, please investigate (perhaps version of uplink-linux-1.6.0-2_i386-1344894496.deb?)
      Problem: couldn't figure out uplink-1.6-1.i386.rpm, please investigate (perhaps version of uplink-linux-1.0.0-1.fc17.i686-1344894496.rpm?)
      Problem: couldn't verify that cavestoryplus-linux-1324519044.tar.gz was cave_story_plus-linux-r100.tar.bz2 ("git annex get" and retry)
      Problem: couldn't verify that gsb1324679796.sh was GSB-final.sh ("git annex get" and retry)

    Will perform these actions:
      Download closure-windows-1355458142.zip to Games/Closure/Windows - i386/closure-windows-1355458142.zip
      Download closure-mac-1355458142.zip to Games/Closure/OSX/closure-mac-1355458142.zip
      Download Closure-Linux-1.1-2012-12-18.sh to Games/Closure/Linux - i386/Closure-Linux-1.1-2012-12-18.sh
      Download christopher_rhyne_-_closure_-_original_soundtrack-mp3.zip to Games/Closure/Soundtrack/christopher_rhyne_-_closure_-_original_soundtrack-mp3.zip
      Download christopher_rhyne_-_closure_-_original_soundtrack-flac.zip to Games/Closure/Soundtrack/christopher_rhyne_-_closure_-_original_soundtrack-flac.zip
      Download dungeon_defenders-windows-1355435306.zip to Games/Dungeon Defenders + All DLC/Windows - i386/dungeon_defenders-windows-1355435306.zip
      Download dungeon_defenders-mac-1355435306.zip to Games/Dungeon Defenders + All DLC/OSX/dungeon_defenders-mac-1355435306.zip
      Download dundef-linux-12192012.mojo.run to Games/Dungeon Defenders + All DLC/Linux - i386/dundef-linux-12192012.mojo.run
      Download dundef-linux-12182012.tar.bz2 to Games/Dungeon Defenders + All DLC/Linux - i386/dundef-linux-12182012.tar.bz2
      Download afshin_toufighian_-_dungeon_defenders_soundtrack-mp3.zip to Games/Dungeon Defenders + All DLC/Soundtrack/afshin_toufighian_-_dungeon_defenders_soundtrack-mp3.zip
      Download afshin_toufighian_-_dungeon_defenders_soundtrack-flac.zip to Games/Dungeon Defenders + All DLC/Soundtrack/afshin_toufighian_-_dungeon_defenders_soundtrack-flac.zip
      Action: Delete eufloria-android-1.0.2hb-1353553330.apk and replace with version Eufloria-android-1.0.4hb-1355711321.apk
      Download indiegamethemovie_1080p.zip to Videos/Movies/Indie Game - The Movie/indiegamethemovie_1080p.zip
      Download indiegamethemovie_720p.zip to Videos/Movies/Indie Game - The Movie/indiegamethemovie_720p.zip
      Download jim_guthrie_-_indie_game-the_movie-soundtrack-mp3.zip to Videos/Movies/Indie Game - The Movie/Soundtrack/jim_guthrie_-_indie_game-the_movie-soundtrack-mp3.zip
      Download jim_guthrie_-_indie_game-the_movie-soundtrack-flac.zip to Videos/Movies/Indie Game - The Movie/Soundtrack/jim_guthrie_-_indie_game-the_movie-soundtrack-flac.zip
      Download legend_of_grimrock-windows-1.3.6-installer.zip to Games/Legend of Grimrock/Windows - i386/legend_of_grimrock-windows-1.3.6-installer.zip
      Download legend_of_grimrock-mac-1.3.6.dmg to Games/Legend of Grimrock/OSX/legend_of_grimrock-mac-1.3.6.dmg
      Download LegendOfGrimrock-Linux-2012-12-18.sh to Games/Legend of Grimrock/Linux - i386/LegendOfGrimrock-Linux-2012-12-18.sh
      Download legend_of_grimrock_-_soundtrack-mp3.zip to Games/Legend of Grimrock/Soundtrack/legend_of_grimrock_-_soundtrack-mp3.zip
      Download legend_of_grimrock_-_soundtrack-flac.zip to Games/Legend of Grimrock/Soundtrack/legend_of_grimrock_-_soundtrack-flac.zip
      Download machinarium_20121106-ubuntu_i386.deb to Games/Machinarium/Linux - i386/machinarium_20121106-ubuntu_i386.deb
      Download Osmos_1.6.1.x86_64.rpm to Games/Osmos/Linux - i386/Osmos_1.6.1.x86_64.rpm
      Download RevengeOfTheTitans-HIB-18019-amd64.deb to Games/Revenge of the Titans/Linux - i386/RevengeOfTheTitans-HIB-18019-amd64.deb
      Download RevengeOfTheTitans-HIB-18019-amd64.tar.gz to Games/Revenge of the Titans/Linux - i386/RevengeOfTheTitans-HIB-18019-amd64.tar.gz
      Action: Delete rochard-linux-20120927_131RC1_Linux32bit-1348771540.tar.gz and replace with version rochard-linux-20121002_1.32-32bit.tar.gz
      Download rochard-linux-1.32-rc3-1354236999-i386.deb to Games/Rochard/Linux - i386/rochard-linux-1.32-rc3-1354236999-i386.deb
      Action: Delete rochard-linux-20120927_131RC1_Linux64bit-1348771540.tar.gz and replace with version rochard-linux-20121002_1.32-64bit.tar.gz
      Download rochard-linux-1.32_rc3-1354236999-amd64.deb to Games/Rochard/Linux - x86_64/rochard-linux-1.32_rc3-1354236999-amd64.deb
      Download shank2-windows-installer.zip to Games/Shank 2/Windows - i386/shank2-windows-installer.zip
      Download shank2-mac-b10.dmg to Games/Shank 2/OSX/shank2-mac-b10.dmg
      Download shank2-linux-b10.tar.gz to Games/Shank 2/Linux - i386/shank2-linux-b10.tar.gz
      Download shank_2-soundtrack-mp3.zip to Games/Shank 2/Soundtrack/shank_2-soundtrack-mp3.zip
      Download shank_2-soundtrack-flac.zip to Games/Shank 2/Soundtrack/shank_2-soundtrack-flac.zip
      Download snapshot-windows-v28-installer.exe to Games/Snapshot/Windows - i386/snapshot-windows-v28-installer.exe
      Download snapshot-mac-v28.zip to Games/Snapshot/OSX/snapshot-mac-v28.zip
      Download snapshot-linux-28-i386.deb to Games/Snapshot/Linux - i386/snapshot-linux-28-i386.deb
      Download Snapshot-linux-v28-x86.tar.gz to Games/Snapshot/Linux - i386/Snapshot-linux-v28-x86.tar.gz
      Download snapshot-linux-28-amd64.deb to Games/Snapshot/Linux - x86_64/snapshot-linux-28-amd64.deb
      Download Snapshot-linux-v28-x64.tar.gz to Games/Snapshot/Linux - x86_64/Snapshot-linux-v28-x64.tar.gz
      Download snapshot-soundtrack-mp3.zip to Games/Snapshot/Soundtrack/snapshot-soundtrack-mp3.zip
      Download snapshot-soundtrack-flac.zip to Games/Snapshot/Soundtrack/snapshot-soundtrack-flac.zip
      Action: Delete spirits-windows-1.0.0-1344892417.zip and replace with version spirits-windows-1.0.1-1348705231.zip
      Action: Delete spirits-linux-1.0.0-120719-1344640830.zip and replace with version spirits-linux-1.0.1_120903-1348705231.zip
      Action: Delete splice-mac-1353389454.zip and replace with version splice-mac-1355772202.zip
      Download splice-linux-1353389454-amd64.deb to Games/Splice/Linux - x86_64/splice-linux-1353389454-amd64.deb
      Download splice-linux-1353389454-i386.deb to Games/Splice/Linux - i386/splice-linux-1353389454-i386.deb
      Download steel-storm-burning-retribution_2.00.02818_amd64.deb to Games/Steel Storm - Burning Retribution/Linux - i386/steel-storm-burning-retribution_2.00.02818_amd64.deb
      Action: Delete sword_and_sworcery-android-1.0.7.1hb-1352529370.apk and replace with version swordandsworcery-android-1.0.8hb-1355269657.apk
      Download the_binding_of_isaac_wrath_of_the_lamb-windows-1.48-1355437751.zip to Games/Binding of Isaac + Wrath of the Lamb DLC/Windows - i386/the_binding_of_isaac_wrath_of_the_lamb-windows-1.48-1355437751.zip
      Download the_binding_of_isaac_wrath_of_the_lamb-mac.zip to Games/Binding of Isaac + Wrath of the Lamb DLC/OSX/the_binding_of_isaac_wrath_of_the_lamb-mac.zip
      Download the_binding_of_isaac_wrath_of_the_lamb-linux-1.48-1355426233.swf.zip to Games/Binding of Isaac + Wrath of the Lamb DLC/Flash/the_binding_of_isaac_wrath_of_the_lamb-linux-1.48-1355426233.swf.zip
      Download the_binding_of_isaac_wrath_of_the_lamb-linux-20121219-i386.deb to Games/Binding of Isaac + Wrath of the Lamb DLC/Linux - i386/the_binding_of_isaac_wrath_of_the_lamb-linux-20121219-i386.deb
      Download the_binding_of_isaac_wrath_of_the_lamb-linux.tar.gz to Games/Binding of Isaac + Wrath of the Lamb DLC/Linux - i386/the_binding_of_isaac_wrath_of_the_lamb-linux.tar.gz
      Action: Delete Torchlight-2012-09-24.sh and replace with version Torchlight-2012-09-26.sh
      Download vessel-12082012-bin to Games/Vessel/Linux - i386/vessel-12082012-bin
      Action: Delete voxatron_0.2.1_amd64.deb and replace with version voxatron_0.2.2_amd64.deb
      Action: Rename wizorb-64bit.tar.gv to wizorb-64bit.tar.gz

    Does this seem right? [y/N]

Humbug's output is roughly divisible into problems and
actions. Actions represent situations that Humbug knows how to
handle. Problems represent situations that Humbug can't or won't
handle.

Let's look at the actions first.

- In this example, you can see from the lines starting "Download
  splice-135338954-amd64.deb" that Humbug knows that I don't already
  have the .deb versions of Splice for either 32-bit or 64-bit
  Linux. (Previously, Splice was only offered as a .tar.gz.)
- You can see from the line "Action: Delete voxatron_0.2.1_amd64.deb
  and replace with version voxatron_0.2.2_amd64.deb" that Humbug
  noticed that the version of Voxatron I have is outdated. Since
  version 0.2.2 is newer than 0.2.1, Humbug can sight-unseen erase
  0.2.1. What's new is *always* better than what's old!
- You can see from the line "Action: Rename wizorb-64bit.tar.gv to
  wizorb-64bit.tar.gz" that Humbug found a file called
  ``wizorb-64bit.tar.gv``, which corresponds to the Humble Bundle file
  called ``wizorb-64bit.tar.gz``. I probably typoed the name when I
  was managing things by hand. Humbug compared the md5s and found that
  the files were the same, so it will rename the file for me.

If I answer "y" at the prompt, all the above actions will be taken and
committed individually. (If I want, I can squish them down using
normal branch/merge techniques.)

Now, problems:

- One kind of problem is when Humbug sees a link in the HTML that
  doesn't link to a file. The "Stream" links for movies, for example,
  aren't downloadable, and neither is the "Coming shortly" link for
  Vessel. Humbug also doesn't know how to handle the "Soundtrack
  website" link for the World of Goo soundtrack, so I'll have to deal
  with that manually.
- Another kind of problem is when Humbug tries to match your files to
  the files on the Humble Bundle page and finds a version that you
  have that the Humble Bundle doesn't offer. In this example, I seem
  to have an i386 .rpm version of Crayon Physics Deluxe. I have no
  idea where I got it. The Humble Indie Bundle people haven't told me
  why they aren't offering it any more -- maybe that version had a bug
  or wasn't compiled correctly or something -- and Humbug doesn't know
  what to do with it, so it's letting me know.
- When Humbug finds a link that looks like it could match a file in
  your annex, it tries to compare it. If, however, the file isn't
  present in this repo, Humbug can't compare the MD5s to figure out
  whether the file is the same or not. If you "git annex get" these
  files to copy them to your current repo and rerun Humbug, it will
  compare them.
- Finally, if Humbug compares the files and the MD5s don't match, it
  complains "couldn't figure out". In this example, it saw that the
  32-bit .deb version of Uplink 1.6.0-2 was available, but I have
  version 1.6-1. It didn't recognize that the remote version was
  newer, so complained. It also saw that the 32-bit .rpm 1.0.0-1 is
  available, but I have 1.6-1. It seems like the Humble Bundle version
  is older, so it got confused. The first of these is a bug in Humbug
  (and can be reported as such). The second might be an error on the
  Humble Bundle site. Both can be dealt with manually, or not at all.

If Humbug finds a problem with one of the files in a directory, it
refuses to take any actions on that directory for fear of making
things worse. In this example, there are two links to the Machinarium
soundtrack, one in MP3 and one in FLAC, and there is one soundtrack
present already, but since Humbug can't find out which one the
existing version is, it refuses to download either.

Caveats
-------

Humbug was developed around my already-existing Annex, which contains
a bunch of games that I downloaded and maintained in a very ad-hoc
manner. As a result it probably won't work for *your* Annex or an
empty annex. Patches welcome, particularly to add a configuration file
interface in an XDG-compatible location!

Humbug's support for unpacking zips is pretty fiddly. Expect it to
just crash. You'll get to clean it up by hand.
