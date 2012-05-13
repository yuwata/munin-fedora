Name:      munin
Version:   1.4.7
Release:   4%{?dist}
Summary:   Network-wide graphing framework (grapher/gatherer)
License:   GPLv2 and Bitstream Vera
Group:     System Environment/Daemons
URL:       http://munin.projects.linpro.no/

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Source0: http://downloads.sourceforge.net/sourceforge/munin/%{name}-%{version}.tar.gz
Source10: http://downloads.sourceforge.net/sourceforge/munin/%{name}-%{version}.tar.gz.sha256sum

Patch1: munin-1.4.6-restorecon.patch
Patch2: munin-1.4.2-fontfix.patch

Source1: munin-1.2.4-sendmail-config
Source2: munin-1.2.5-hddtemp_smartctl-config
Source3: munin-node.logrotate
Source4: munin.logrotate
Source6: munin-1.2.6-postfix-config
Source7: munin-1.4.5-df-config
Source8: munin-node.service
Source9: %{name}.conf
Source11: munin-node.service-privatetmp

BuildArchitectures: noarch

BuildRequires: perl-Module-Build
# needed for hostname for the defaut config
BuildRequires: net-tools
BuildRequires: perl-HTML-Template
BuildRequires: perl-Log-Log4perl
BuildRequires: perl-Net-Server
BuildRequires: perl-Net-SSLeay
BuildRequires: perl-Net-SNMP

# java buildrequires on fedora < 17 and rhel 
%if 0%{?rhel} > 4 || 0%{?fedora} < 17
BuildRequires: java-1.6.0-devel
BuildRequires: mx4j
BuildRequires: jpackage-utils
%endif

# java buildrequires on fedora 17 and higher
%if 0%{?fedora} > 16
BuildRequires: java-1.7.0-devel
BuildRequires: mx4j
BuildRequires: jpackage-utils
%endif

%if 0%{?rhel} > 6 || 0%{?fedora} > 15
BuildRequires: systemd-units
%endif

Requires: %{name}-common = %{version}
Requires: perl-Net-Server
Requires: perl-Net-SNMP
Requires: rrdtool
Requires: logrotate
Requires: /bin/mail
Requires(pre): shadow-utils
Requires: perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))
%if 0%{?rhel} > 5 || 0%{?fedora} > 6
Requires: dejavu-sans-mono-fonts
%else
Requires: bitstream-vera-fonts
%endif

%description
Munin is a highly flexible and powerful solution used to create graphs of
virtually everything imaginable throughout your network, while still
maintaining a rattling ease of installation and configuration.

This package contains the grapher/gatherer. You will only need one instance of
it in your network. It will periodically poll all the nodes in your network
it's aware of for data, which it in turn will use to create graphs and HTML
pages, suitable for viewing with your graphical web browser of choice.

Munin is written in Perl, and relies heavily on Tobi Oetiker's excellent
RRDtool.

%package node
Group: System Environment/Daemons
Summary: Network-wide graphing framework (node)
BuildArchitectures: noarch
Requires: %{name}-common = %{version}
Requires: perl-Net-Server
Requires: procps >= 2.0.7
Requires: sysstat, /usr/bin/which, hdparm
Requires(pre): shadow-utils
Requires(post): /sbin/chkconfig
Requires(preun): /sbin/chkconfig
Requires(preun): /sbin/service
Requires: perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))

%description node
Munin is a highly flexible and powerful solution used to create graphs of
virtually everything imaginable throughout your network, while still
maintaining a rattling ease of installation and configuration.

This package contains node software. You should install it on all the nodes
in your network. It will know how to extract all sorts of data from the
node it runs on, and will wait for the gatherer to request this data for
further processing.

It includes a range of plugins capable of extracting common values such as
cpu usage, network usage, load average, and so on. Creating your own plugins
which are capable of extracting other system-specific values is very easy,
and is often done in a matter of minutes. You can also create plugins which
relay information from other devices in your network that can't run Munin,
such as a switch or a server running another operating system, by using
SNMP or similar technology.

Munin is written in Perl, and relies heavily on Tobi Oetiker's excellent
RRDtool.

%package common
Group: System Environment/Daemons
Summary: Network-wide graphing framework (common files)
BuildArchitectures: noarch
Requires: perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))

%description common
Munin is a highly flexible and powerful solution used to create graphs of
virtually everything imaginable throughout your network, while still
maintaining a rattling ease of installation and configuration.

This package contains common files that are used by both the server (munin)
and node (munin-node) packages.

%if 0%{?rhel} > 4 || 0%{?fedora} > 6
%package java-plugins
Group: System Environment/Daemons
Summary: java-plugins for munin
Requires: %{name}-node = %{version}
BuildArchitectures: noarch

%description java-plugins
java-plugins for munin-node.
%endif

%prep
%setup -q
%patch1 -p1

%if 0%{?rhel} < 6 && 0%{?fedora} < 11
%patch2 -p0
%endif

%build
%if 0%{?rhel} > 4 || 0%{?fedora} > 6
export  CLASSPATH=plugins/javalib/org/munin/plugin/jmx:$(build-classpath mx4j):$CLASSPATH
%endif
make    CONFIG=dists/redhat/Makefile.config

%install

## Node
make    CONFIG=dists/redhat/Makefile.config \
%if 0%{?rhel} > 4 || 0%{?fedora} > 6
        JAVALIBDIR=%{buildroot}%{_datadir}/java \
%endif
        PREFIX=%{buildroot}%{_prefix} \
        DOCDIR=%{buildroot}%{_docdir}/%{name}-%{version} \
        MANDIR=%{buildroot}%{_mandir} \
        DESTDIR=%{buildroot} \
        install

mkdir -p %{buildroot}/etc/munin/plugins
mkdir -p %{buildroot}/etc/munin/node.d
mkdir -p %{buildroot}/etc/munin/plugin-conf.d
mkdir -p %{buildroot}/etc/munin/conf.d
mkdir -p %{buildroot}/etc/logrotate.d
mkdir -p %{buildroot}/var/lib/munin
mkdir -p %{buildroot}/var/log/munin

# Fix default config file
sed -i 's,/etc/munin/munin-conf.d,/etc/munin/conf.d,' %{buildroot}/etc/munin/munin.conf

#
# don't enable munin-node by default.
#
%if 0%{?rhel} > 6 || 0%{?fedora} > 15
mkdir -p %{buildroot}/lib/systemd/system/
%endif
# Fedora 17 and higer uses privatetmp
%if 0%{?fedora} > 16
install -m 0644 %{SOURCE11} %{buildroot}/lib/systemd/system/munin-node.service
%endif

%if 0%{?fedora} > 15 && 0%{?fedora} < 17
# Fedora 16 does not use privatetmp
install -m 0644 %{SOURCE8} %{buildroot}/lib/systemd/system/munin-node.service
%endif
%if 0%{?rhel} > 4 || 0%{?fedora} < 16
# Fedora 15 and rhel use sysvinit
mkdir -p %{buildroot}/etc/rc.d/init.d
cat dists/redhat/munin-node.rc | sed -e 's/2345/\-/' > %{buildroot}/etc/rc.d/init.d/munin-node
chmod 755 %{buildroot}/etc/rc.d/init.d/munin-node
%endif

%if 0%{?rhel} > 6 || 0%{?fedora} > 14
mkdir -p %{buildroot}%{_sysconfdir}/tmpfiles.d
install -m 0644 %{SOURCE9} %{buildroot}%{_sysconfdir}/tmpfiles.d/%{name}.conf
%endif

install -m0644 dists/tarball/plugins.conf %{buildroot}/etc/munin/plugin-conf.d/munin-node

#
# remove the Sybase plugin for now, as they need perl modules
# that are not in extras. We can readd them when/if those modules are added.
#
rm -f %{buildroot}/usr/share/munin/plugins/sybase_space

## Server

mkdir -p %{buildroot}/var/www/html/munin
mkdir -p %{buildroot}/var/log/munin
mkdir -p %{buildroot}/etc/cron.d
mkdir -p %{buildroot}%{_docdir}/%{name}-%{version}

install -m 0644 dists/redhat/munin.cron.d %{buildroot}/etc/cron.d/munin
cp -a master/www/* %{buildroot}/var/www/html/munin/

# install config for sendmail under fedora
install -m 0644 %{SOURCE1} %{buildroot}/etc/munin/plugin-conf.d/sendmail
# install config for hddtemp_smartctl
install -m 0644 %{SOURCE2} %{buildroot}/etc/munin/plugin-conf.d/hddtemp_smartctl
# install logrotate scripts
install -m 0644 %{SOURCE3} %{buildroot}/etc/logrotate.d/munin-node
install -m 0644 %{SOURCE4} %{buildroot}/etc/logrotate.d/munin
# install config for postfix under fedora
install -m 0644 %{SOURCE6} %{buildroot}/etc/munin/plugin-conf.d/postfix
# install df config to exclude fses we shouldn't try and monitor
install -m 0644 %{SOURCE7} %{buildroot}/etc/munin/plugin-conf.d/df
# Create for BZ 786030
touch %{buildroot}/var/lib/munin/plugin-state/yum.state

# Fix path in java plugin
sed -i 's,/opt/munin/lib/munin-jmx-plugins.jar,/usr/share/java/munin-jmx-plugins.jar,g' %{buildroot}/usr/share/munin/plugins/jmx_

# Use system font
rm -f $RPM_BUILD_ROOT/%{_datadir}/munin/DejaVuSansMono.ttf
rm -f $RPM_BUILD_ROOT/%{_datadir}/munin/DejaVuSans.ttf

%clean
rm -rf $RPM_BUILD_ROOT

#
# node package scripts
#
%pre node
getent group munin >/dev/null || groupadd -r munin
getent passwd munin >/dev/null || \
useradd -r -g munin -d /var/lib/munin -s /sbin/nologin \
    -c "Munin user" munin
exit 0

%post node
# sysvinit only in f15 and older and epel
%if 0%{?fedora} < 16 || 0%{?rhel} > 4
/sbin/chkconfig --add munin-node
%endif
# Only run configure on a new install, not an upgrade.
if [ "$1" = "1" ]; then
     /usr/sbin/munin-node-configure --shell 2> /dev/null | sh >& /dev/null || :
fi

%preun node
%if 0%{?rhel} > 6 || 0%{?fedora} > 15
test "$1" != 0 || %{_bindir}/systemctl disable munin-node.service || :
%else
test "$1" != 0 || %{_initrddir}/munin-node stop &>/dev/null || :
test "$1" != 0 || /sbin/chkconfig --del munin-node
%endif

%postun node
if [ "$1" = "0" ]; then
     find /etc/munin/plugins/ -maxdepth 1 -type l -print0 |xargs -0 rm || :
fi

%triggerun node -- munin-node < 1.4.7-2
mv -f %{_sysconfdir}/munin/plugins %{_sysconfdir}/munin/plugins.bak || :

%triggerpostun node -- munin-node < 1.4.7-2
mv -f %{_sysconfdir}/munin/plugins.bak %{_sysconfdir}/munin/plugins || :

#
# main package scripts
#
%pre
getent group munin >/dev/null || groupadd -r munin
getent passwd munin >/dev/null || \
useradd -r -g munin -d /var/lib/munin -s /sbin/nologin \
    -c "Munin user" munin
exit 0

%files
%defattr(-, root, root)
%doc %{_docdir}/%{name}-%{version}/
%{_bindir}/munin-cron
%{_bindir}/munindoc
%{_bindir}/munin-check
%dir %{_datadir}/munin
%{_datadir}/munin/munin-graph
%{_datadir}/munin/munin-html
%{_datadir}/munin/munin-limits
%{_datadir}/munin/munin-update
%{perl_vendorlib}/Munin/Master
%dir /etc/munin/templates
%dir /etc/munin
%dir /etc/munin/conf.d
%config(noreplace) /etc/munin/templates/*
%config(noreplace) /etc/cron.d/munin
%config(noreplace) /etc/munin/munin.conf
%config(noreplace) /etc/logrotate.d/munin
%attr(-, munin, munin) %dir /var/lib/munin
%attr(-, munin, munin) %dir /var/lib/munin/plugin-state
%attr(-, munin, munin) %dir /var/log/munin
%attr(-, munin, munin) /var/www/html/munin
%doc %{_mandir}/man8/munin*
%doc %{_mandir}/man5/munin.conf*

%files node
%defattr(-, root, root)
%config(noreplace) /etc/munin/munin-node.conf
%dir /etc/munin/plugin-conf.d
%dir /etc/munin/node.d
%config(noreplace) /etc/munin/plugin-conf.d/munin-node
%config(noreplace) /etc/munin/plugin-conf.d/sendmail
%config(noreplace) /etc/munin/plugin-conf.d/hddtemp_smartctl
%config(noreplace) /etc/munin/plugin-conf.d/postfix
%config(noreplace) /etc/munin/plugin-conf.d/df
%config(noreplace) /etc/logrotate.d/munin-node
%if 0%{?rhel} > 6 || 0%{?fedora} > 15
/lib/systemd/system/munin-node.service
%else
/etc/rc.d/init.d/munin-node
%endif
%{_sbindir}/munin-run
%{_sbindir}/munin-node
%{_sbindir}/munin-node-configure
%attr(-, munin, munin) %dir /var/log/munin
%dir %{_datadir}/munin
%dir /etc/munin/plugins
%dir /etc/munin
%attr(-, munin, munin) %dir /var/lib/munin
%dir %attr(-, munin, munin) /var/lib/munin/plugin-state
%attr(-, munin, munin) /var/lib/munin/plugin-state/yum.state
%if 0%{?rhel} > 4 || 0%{?fedora} > 6
%exclude %{_datadir}/munin/plugins/jmx_
%endif
%{_datadir}/munin/plugins/
%doc %{_docdir}/%{name}-%{version}/
%doc %{_mandir}/man5/munin-node*
%doc %{_mandir}/man3/Munin*
%doc %{_mandir}/man1/munin*
%{perl_vendorlib}/Munin/Node
%{perl_vendorlib}/Munin/Plugin*

%files common
%defattr(-, root, root)
%doc Announce-1.4.0 ChangeLog COPYING HACKING.pod perltidyrc README RELEASE UPGRADING
%dir %{perl_vendorlib}/Munin
%{perl_vendorlib}/Munin/Common

%attr(-, munin, munin) %dir %{_localstatedir}/run/%{name}/
%if 0%{?rhel} > 6 || 0%{?fedora} > 14
%config(noreplace) %{_sysconfdir}/tmpfiles.d/%{name}.conf
%endif

%if 0%{?rhel} > 4 || 0%{?fedora} > 6
%files java-plugins
%defattr(-, root, root)
%{_datadir}/java/%{name}-jmx-plugins.jar
%{_datadir}/munin/plugins/jmx_
%endif


%changelog
* Sun May 13 2012 Kevin Fenzi <kevin@scrye.com> - 1.4.7-4
- Fix ownership on /var/run/munin. Fixes bug #821204

* Tue Apr 24 2012 Kevin Fenzi <kevin@scrye.com> - 1.4.7-3
- A better for for 811867 with triggers. 
- Fix directory conflict. Fixes bug #816340
- Fix path in java plugin. Fixes bug #816570

* Sun Apr 15 2012 Kevin Fenzi <kevin@scrye.com> - 1.4.7-2
- Fix node postun from messing up plugins on upgrade. Works around bug #811867

* Wed Mar 14 2012 D. Johnson <fenris02@fedoraproject.org> - 1.4.7-1
- updated for 1.4.7 release

* Wed Feb 22 2012 Kevin Fenzi <kevin@scrye.com> 1.4.6-8
- Build against java-1.7.0 now. Fixes bug #796345

* Tue Jan 31 2012 D. Johnson <fenris02@fedoraproject.org> - 1.4.6-7
- Create state file for yum-plugin. Fixes BZ #786030.

* Fri Jan 20 2012 Kevin Fenzi <kevin@scrye.com> - 1.4.6-6
- Add PrivateTmp=true to systemd unit file. Fixes bug #782512
- Change logrotate to use munin user. Fixes bug #771017

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.4.6-5.3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Mon Oct 17 2011 Stanislav Ochotnicky <sochotnicky@redhat.com> - 1.4.6-4.3
- Rebuild for java 1.6.0 downgrade (fesco ticket 663)

* Sat Aug 27 2011 Kevin Fenzi <kevin@scrye.com> - 1.4.6-4.1
- Add patch to run restorecon in the sysvinit script.
- This doesn't matter on f16+

* Sat Aug 20 2011 D. Johnson <fenris02@fedoraproject.org> - 1.4.6-4
- fix tmpfiles.d file for f15 (BZ# 731181)

* Thu Jul 21 2011 Petr Sabata <contyk@redhat.com> - 1.4.6-3
- Perl mass rebuild

* Wed Jul 20 2011 Petr Sabata <contyk@redhat.com> - 1.4.6-2
- Perl mass rebuild

* Wed Jul  8 2011 D. Johnson <fenris02@fedoraproject.org> - 1.4.6-1
- update to 1.4.6

* Fri Jun 17 2011 Marcela Mašláňová <mmaslano@redhat.com> - 1.4.5-13
- Perl mass rebuild

* Wed Jun 15 2011 D. Johnson <fenris02@fedoraproject.org> - 1.4.5-12
- Use tmpfiles.d instead of ExecStartPre
- Add patch for noSuchObject errors (BZ# 712245)

* Fri Jun 10 2011 Marcela Mašláňová <mmaslano@redhat.com> - 1.4.5-11
- Perl 5.14 mass rebuild

* Wed Jun  1 2011 D. Johnson <fenris02@fedoraproject.org> - 1.4.5-10
- Fixes http://munin-monitoring.org/ticket/887

* Mon May 30 2011 D. Johnson <fenris02@fedoraproject.org> - 1.4.5-9
- Native systemd service file for munin-node (BZ# 699275)

* Tue Feb 08 2011 Kevin Fenzi <kevin@tummy.com> - 1.4.5-8
- Fix issue with uppercase node names returning no data. Fixes #673263

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.4.5-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Sun Dec 05 2010 Kevin Fenzi <kevin@tummy.com> - 1.4.5-6
- Adjust the df fix to include all the right fses

* Thu Nov 25 2010 Kevin Fenzi <kevin@tummy.com> - 1.4.5-5
- Exclude some fses from df plugin. fixes #601410

* Wed Aug 11 2010 Todd Zullinger <tmz@pobox.com> - 1.4.5-4.1
- Move jmx_ plugin to java-plugins package

* Wed Jul 07 2010 Kevin Fenzi <kevin@tummy.com> - 1.4.5-4
- Move docs to common subpackage to make sure COPYING is installed.

* Sat Jul 03 2010 Kevin Fenzi <kevin@tummy.com> - 1.4.5-3
- Add /etc/munin/node.d dir

* Sat Jun 12 2010 Kevin Fenzi <kevin@tummy.com> - 1.4.5-2
- Add /etc/munin/conf.d/ dir

* Sat Jun 05 2010 Kevin Fenzi <kevin@tummy.com> - 1.4.5-1
- Update to 1.4.5

* Tue Jun 01 2010 Marcela Maslanova <mmaslano@redhat.com> - 1.4.4-2
- Mass rebuild with perl-5.12.0

* Mon Mar 01 2010 Kevin Fenzi <kevin@tummy.com> - 1.4.4-1
- Update to 1.4.4
- Add more doc files. Fixes bug #563824
- fw_forwarded_local fixed upstream in 1.4.4. Fixes bug #568500

* Sun Jan 17 2010 Kevin Fenzi <kevin@tummy.com> - 1.4.3-2
- Fix owner on state files.
- Add some BuildRequires.
- Make munin-node-configure only run on install, not upgrade. bug 540687

* Thu Dec 31 2009 Kevin Fenzi <kevin@tummy.com> - 1.4.3-1
- Update to 1.4.3

* Thu Dec 17 2009 Ingvar Hagelund <ingvar@linpro.no> - 1.4.2-1
- New upstream release
- Removed upstream packaged fonts
- Added a patch that makes rrdtool use the system bitstream vera fonts on
  rhel < 6 and fedora < 11

* Fri Dec 11 2009 Ingvar Hagelund <ingvar@linpro.no> - 1.4.1-3
- More correct fedora and el versions for previous font path fix
- Added a patch that fixes a quoting bug in GraphOld.pm, fixing fonts on el4

* Wed Dec 09 2009 Ingvar Hagelund <ingvar@linpro.no> - 1.4.1-2
- Remove jmx plugins when not supported (like on el4 and older fedora)
- Correct font path on older distros like el5, el4 and fedora<11

* Fri Dec 04 2009 Kevin Fenzi <kevin@tummy.com> - 1.4.1-1
- Update to 1.4.1

* Sat Nov 28 2009 Kevin Fenzi <kevin@tummy.com> - 1.4.0-1
- Update to final 1.4.0 version

* Sat Nov 21 2009 Kevin Fenzi <kevin@tummy.com> - 1.4.0-0.1.beta
- Update to beta 1.4.0 version.
- Add common subpackage for common files.

* Sun Nov 08 2009 Kevin Fenzi <kevin@tummy.com> - 1.4.0-0.1.alpha
- Initial alpha version of 1.4.0

* Sat Jul 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.6-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.6-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Sat Jan 24 2009 Andreas Thienemann <andreas@bawue.net> - 1.2.6-8
- Updated dependencies to better reflect plugin requirements
- Added hddtemp_smartctl patch to only scan for standby state on /dev/[sh]d? devices.

* Sat Jan 17 2009 Kevin Fenzi <kevin@tummy.com> - 1.2.6-7
- Adjust font requires for new dejavu-sans-mono-fonts name (fixes #480463)

* Mon Jan 12 2009 Kevin Fenzi <kevin@tummy.com> - 1.2.6-6
- Fix to require the correct font

* Sun Jan 11 2009 Kevin Fenzi <kevin@tummy.com> - 1.2.6-5
- Switch to using dejavu-fonts instead of bitstream-vera

* Sun Jan 04 2009 Kevin Fenzi <kevin@tummy.com> - 1.2.6-4
- Require bitstream-vera-fonts-sans-mono for Font (fixes #477428)

* Mon Aug 11 2008 Kevin Fenzi <kevin@tummy.com> - 1.2.6-3
- Move Munin/Plugin.pm to the node subpackage (fixes #457403)

* Sat Jul 12 2008 Kevin Fenzi <kevin@tummy.com> - 1.2.6-2
- Apply postfix patch (fixes #454159)
- Add perl version dep and remove unneeded perl-HTML-Template (fixes #453923)

* Fri Jun 20 2008 Kevin Fenzi <kevin@tummy.com> - 1.2.6-1
- Upgrade to 1.2.6

* Tue May 20 2008 Kevin Fenzi <kevin@tummy.com> - 1.2.5-5
- Rebuild for new perl

* Wed Dec 26 2007 Kevin Fenzi <kevin@tummy.com> - 1.2.5-4
- Add patch to fix ampersand and degrees in plugins (fixes #376441)

* Fri Nov 30 2007 Kevin Fenzi <kevin@tummy.com> - 1.2.5-3
- Removed unnneeded plugins.conf file (fixes #288541)
- Fix license tag.
- Fix ip_conntrack monitoring (fixes #253192)
- Switch to new useradd guidelines.

* Tue Mar 27 2007 Kevin Fenzi <kevin@tummy.com> - 1.2.5-2
- Fix directory ownership (fixes #233886)

* Tue Oct 17 2006 Kevin Fenzi <kevin@tummy.com> - 1.2.5-1
- Update to 1.2.5
- Fix HD stats (fixes #205042)
- Add in logrotate scripts that seem to have been dropped upstream

* Sun Aug 27 2006 Kevin Fenzi <kevin@tummy.com> - 1.2.4-10
- Rebuild for fc6

* Tue Jun 27 2006 Kevin Fenzi <kevin@tummy.com> - 1.2.4-9
- Re-enable snmp plugins now that perl-Net-SNMP is available (fixes 196588)
- Thanks to Herbert Straub <herbert@linuxhacker.at> for patch.
- Fix sendmail plugins to look in the right place for the queue

* Sat Apr 22 2006 Kevin Fenzi <kevin@tummy.com> - 1.2.4-8
- add patch to remove unneeded munin-nagios in cron.
- add patch to remove buildhostname in munin.conf (fixes #188928)
- clean up prep section of spec.

* Fri Feb 24 2006 Kevin Fenzi <kevin@scrye.com> - 1.2.4-7
- Remove bogus Provides for perl RRDs (fixes #182702)

* Thu Feb 16 2006 Kevin Fenzi <kevin@tummy.com> - 1.2.4-6
- Readded old changelog entries per request
- Rebuilt for fc5

* Sat Dec 24 2005 Kevin Fenzi <kevin@tummy.com> - 1.2.4-5
- Fixed ownership for /var/log/munin in node subpackage (fixes 176529)

* Wed Dec 14 2005 Kevin Fenzi <kevin@tummy.com> - 1.2.4-4
- Fixed ownership for /var/lib/munin in node subpackage

* Wed Dec 14 2005 Kevin Fenzi <kevin@tummy.com> - 1.2.4-3
- Fixed libdir messup to allow builds on x86_64

* Mon Dec 12 2005 Kevin Fenzi <kevin@tummy.com> - 1.2.4-2
- Removed plugins that require Net-SNMP and Sybase

* Tue Dec  6 2005 Kevin Fenzi <kevin@tummy.com> - 1.2.4-1
- Inital cleanup for fedora-extras

* Thu Apr 21 2005 Ingvar Hagelund <ingvar@linpro.no> - 1.2.3-4
- Fixed a bug in the iostat plugin

* Wed Apr 20 2005 Ingvar Hagelund <ingvar@linpro.no> - 1.2.3-3
- Added the missing /var/run/munin

* Tue Apr 19 2005 Ingvar Hagelund <ingvar@linpro.no> - 1.2.3-2
- Removed a lot of unecessary perl dependencies

* Mon Apr 18 2005 Ingvar Hagelund <ingvar@linpro.no> - 1.2.3-1
- Sync with svn

* Tue Mar 22 2005 Ingvar Hagelund <ingvar@linpro.no> - 1.2.2-5
- Sync with release of 1.2.2
- Add some nice text from the suse specfile
- Minimal changes in the header
- Some cosmetic changes
- Added logrotate scripts (stolen from debian package)

* Sun Feb 01 2004 Ingvar Hagelund <ingvar@linpro.no>
- Sync with CVS. Version 1.0.0pre2

* Sun Jan 18 2004 Ingvar Hagelund <ingvar@linpro.no>
- Sync with CVS. Change names to munin.

* Fri Oct 31 2003 Ingvar Hagelund <ingvar@linpro.no>
- Lot of small fixes. Now builds on more RPM distros

* Wed May 21 2003 Ingvar Hagelund <ingvar@linpro.no>
- Sync with CVS
- 0.9.5-1

* Tue Apr  1 2003 Ingvar Hagelund <ingvar@linpro.no>
- Sync with CVS
- Makefile-based install of core files
- Build doc (only pod2man)

* Thu Jan  9 2003 Ingvar Hagelund <ingvar@linpro.no>
- Sync with CVS, auto rpmbuild

* Thu Jan  2 2003 Ingvar Hagelund <ingvar@linpro.no>
- Fix spec file for RedHat 8.0 and new version of lrrd

* Wed Sep  4 2002 Ingvar Hagelund <ingvar@linpro.no>
- Small bugfixes in the rpm package

* Tue Jun 18 2002 Kjetil Torgrim Homme <kjetilho@linpro.no>
- new package
