# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	smp		# don't build SMP module
%bcond_without	userspace	# don't build userspace module
%bcond_with	verbose		# verbose build (V=1)


#
# main package.
#
%define module net-rt2400
Name:           kernel-net-rt2400
Version:        1.1.1
%define _rel    0.b1.0.1
Release:        %{_rel}@%{_kernel_ver_str}
License:        MPL or GPL
# Source0:      http://www.minitar.com/downloads/rt2400_linux-%{version}-b1.tgz
Source0:        http://dl.sf.net/rt2400/rt2400-%{version}-b1.tar.gz
# Source0-md5:  bb0b34ebb9a39f3313aaf8e976e99ca1
# URL:          http://www.minitar.com
URL:            http://rt2400.sourceforge.net/
Group:          Base/Kernel
BuildRoot:      %{tmpdir}/%{name}-%{version}-root-%(id -u -n)
%if %{with kernel}
%{?with_dist_kernel:BuildRequires:	kernel-module-build >= 2.6.7}
BuildRequires:	rpmbuild(macros) >= 1.153
%endif

Summary:	Linux driver for WLAN card base on RT2400
Summary(pl):	Sterownik dla Linuksa do kart bezprzewodowych na uk3adzie RT2400
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_up}
Requires(post,postun):	/sbin/depmod

%description -n kernel-%{module}
This is driver for ... for Linux.

This package contains Linux module.

%description -n kernel-net-rt2400 -l pl
Sterownik dla Linuksa do ...

Ten pakiet zawiera modu³ j±dra Linuksa.

%package -n kernel-smp-%{module}
Summary:	Linux SMP driver for ...
Summary(pl):	Sterownik dla Linuksa SMP do ...
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_smp}
Requires(post,postun):	/sbin/depmod

%description -n kernel-smp-%{module}
This is driver for ... for Linux.

This package contains Linux SMP module.

%description -n kernel-smp-%{module} -l pl
Sterownik dla Linuksa do ...

Ten pakiet zawiera modu³ j±dra Linuksa SMP.

%build
%if %{with userspace}


%endif

%if %{with kernel}
# kernel module(s)
for cfg in %{?with_dist_kernel:%{?with_smp:smp} up}%{!?with_dist_kernel:nondist}; do
    if [ ! -r "%{_kernelsrcdir}/config-$cfg" ]; then
	exit 1
    fi
    rm -rf include
    install -d include/{linux,config}
    ln -sf %{_kernelsrcdir}/config-$cfg .config
    ln -sf %{_kernelsrcdir}/include/linux/autoconf-$cfg.h include/linux/autoconf.h
    ln -sf %{_kernelsrcdir}/include/asm-%{_target_base_arch} include/asm
    touch include/config/MARKER
#
#	patching/creating makefile(s) (optional)
#
    %{__make} -C %{_kernelsrcdir} clean modules \
	RCS_FIND_IGNORE="-name '*.ko' -o" \
	M=$PWD O=$PWD \
	%{?with_verbose:V=1}
    mv $mod_name{,-$cfg}.ko
done
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with userspace}


%endif

%if %{with kernel}
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}{,smp}/$dir
install $mod_name-%{?with_dist_kernel:up}%{!?with_dist_kernel:nondist}.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/$dir/$mod_name.ko
%if %{with smp} && %{with dist_kernel}
install $mod_name-smp.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/$dir/$mod_name.ko
%endif
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post
%depmod %{_kernel_ver}

%postun
%depmod %{_kernel_ver}

%post -n kernel-smp-%{module}
%depmod %{_kernel_ver}

%postun -n kernel-smp-%{module}
%depmod %{_kernel_ver}

%if %{with kernel}
%files -n kernel-%{module}
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/$dir/*.ko*

%if %{with smp} && %{with dist_kernel}
%files -n kernel-smp-%{module}
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}smp/$dir/*.ko*
%endif
%endif

%if %{with userspace}
#%%files ...
%defattr(644,root,root,755)

%endif
