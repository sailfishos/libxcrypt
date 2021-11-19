# Based on Fedoras libxcrypt.spec with changes to
# + %%{?fedora macros removed/replaced}
# + Mentions of hwmac/fips removed
# + Handling of Fedora's legacy libcrypt packaging removed

# Build with new api?
%bcond_without libxcrypt_new_api

# Build the compat package?
%bcond_with libxcrypt_compat_pkg

# Replace obsolete functions with a stub?
%bcond_with    libxcrypt_enosys_stubs


# We don't have this currently just define it
%global _vpath_builddir build

# Shared object version of libcrypt.
%if %{with libxcrypt_new_api}
%global soc  2
%global sol  0
%global sof  0
%global sov  %{soc}.%{sol}.%{sof}
%else
%global soc  1
%global sol  1
%global sof  0
%global sov  %{soc}.%{sol}.%{sof}
%endif

%if %{with libxcrypt_compat_pkg}
%global csoc 1
%global csol 1
%global csof 0
%global csov %{csoc}.%{csol}.%{csof}
%endif


# First version of glibc built without libcrypt.
%global glibc_minver     2.27


# The libxcrypt-devel package conflicts with out-dated manuals
# shipped with the man-pages packages *before* this EVR.
%global man_pages_minver 4.15-3


# Hash methods and API supported by libcrypt.
# NEVER EVER touch this, if you do NOT know what you are doing!
%global hash_methods   all

%if %{with libxcrypt_new_api}
%global obsolete_api   no
%else
%global obsolete_api   glibc
%endif

%if %{with libxcrypt_compat_pkg}
%global compat_methods all
%global compat_api     glibc
%endif


# Do we replace the obsolete API functions with stubs?
%if %{with libxcrypt_enosys_stubs}
%global enosys_stubs   yes
%else
%global enosys_stubs   no
%endif


#
# Needed for the distribution README file.
%global distname .sailfishos


# Needed for out-of-tree builds.
%global _configure "$(realpath ../configure)"


# Common configure options.
%global common_configure_options           \\\
  --disable-failure-tokens                 \\\
  --disable-silent-rules                   \\\
  --enable-shared                          \\\
%if %{with staticlib}                      \
  --enable-static                          \\\
%else                                      \
  --disable-static                         \\\
%endif                                     \
  --disable-valgrind                       \\\
  --srcdir=$(realpath ..)                  \\\
  --with-pkgconfigdir=%{_libdir}/pkgconfig

# Fail linking if there are undefined symbols.
# Required for proper ELF symbol versioning support.
%global _ld_strict_symbol_defs 1

Name:           libxcrypt
Version:        4.4.23
Release:        1
Summary:        Extended crypt library for descrypt, md5crypt, bcrypt, and others

# For explicit license breakdown, see the
# LICENSING file in the source tarball.
License:        LGPLv2+ and BSD and Public Domain
URL:            https://github.com/besser82/%{name}
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz

# Patch 0000 - 2999: Backported patches from upstream.

# Patch 3000 - 5999: Backported patches from pull requests.

# Patch 6000 - 9999: Downstream patches.

BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  gcc
BuildRequires:  glibc-devel           >= %{glibc_minver}
BuildRequires:  libtool
BuildRequires:  make
# perl-core is a bit to much try just
BuildRequires:  perl

%if %{with libxcrypt_new_api} && %{without libxcrypt_compat_pkg}
Obsoletes:      %{name}-compat         < %{version}-%{release}
%endif

# We need a version of glibc, that doesn't build libcrypt anymore.
Requires:       glibc         >= %{glibc_minver}

%description
libxcrypt is a modern library for one-way hashing of passwords.  It
supports a wide variety of both modern and historical hashing methods:
yescrypt, gost-yescrypt, scrypt, bcrypt, sha512crypt, sha256crypt,
md5crypt, SunMD5, sha1crypt, NT, bsdicrypt, bigcrypt, and descrypt.
It provides the traditional Unix crypt and crypt_r interfaces, as well
as a set of extended interfaces pioneered by Openwall Linux, crypt_rn,
crypt_ra, crypt_gensalt, crypt_gensalt_rn, and crypt_gensalt_ra.

libxcrypt is intended to be used by login(1), passwd(1), and other
similar programs; that is, to hash a small number of passwords during
an interactive authentication dialogue with a human. It is not suitable
for use in bulk password-cracking applications, or in any other situation
where speed is more important than careful handling of sensitive data.
However, it is intended to be fast and lightweight enough for use in
servers that must field thousands of login attempts per minute.
%if %{with libxcrypt_new_api}
This version of the library does not provide the legacy API functions
that have been provided by glibc's libcrypt.so.1.
%endif


%if %{with libxcrypt_compat_pkg}
%package        compat
Summary:        Compatibility library providing legacy API functions

# For testing the glibc compatibility symbols.
#BuildRequires:  libxcrypt-compat

Requires:       %{name}%{?_isa}        = %{version}-%{release}
Requires:       glibc%{?_isa}         >= %{glibc_minver}

%description    compat
This package contains the library providing the compatibility API
for applications that are linked against glibc's libxcrypt, or that
are still using the unsafe and deprecated, encrypt, encrypt_r,
setkey, setkey_r, and fcrypt functions, which are still required by
recent versions of POSIX, the Single UNIX Specification, and various
other standards.

All existing binary executables linked against glibc's libcrypt should
work unmodified with the library supplied by this package.
%endif


%package        devel
Summary:        Development files for %{name}

Conflicts:      man-pages              < %{man_pages_minver}

Requires:       %{name}%{?_isa}        = %{version}-%{release}
Requires:       glibc-devel%{?_isa}   >= %{glibc_minver}

%description    devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.


%if %{with staticlib}
%package        static
Summary:        Static library for -static linking with %{name}

Requires:       %{name}-devel%{?_isa}  = %{version}-%{release}
Requires:       glibc-devel%{?_isa}   >= %{glibc_minver}
Requires:       glibc-static%{?_isa}  >= %{glibc_minver}

%description    static
This package contains the libxcrypt static library for -static
linking.

You don't need this, unless you link statically, which is highly
discouraged.
%endif


%prep
%autosetup -p 1 -n %{name}-%{version}/upstream

$(realpath ./autogen.sh)

%if %{with libxcrypt_new_api}
cat << EOF >> README%{distname}
This version of the %{name} package ships the libcrypt.so.2
library and does not provide the legacy API functions that have
been provided by glibc's libcrypt.so.1.  The removed functions
by name are encrypt, encrypt_r, setkey, setkey_r, and fcrypt.
%if %{with libxcrypt_compat_pkg}

If you are using a third-party application that links against
those functions, or that is linked against glibc's libcrypt,
you may need to install the %{name}-compat package manually.

All existing binary executables linked against glibc's libcrypt
should work unmodified with the libcrypt.so.1 library supplied
by the %{name}-compat package.
%endif
EOF
%endif

%if %{with libxcrypt_enosys_stubs}
cat << EOF >> README.posix
This version of the libcrypt.so.1 library has entirely removed
the functionality of the encrypt, encrypt_r, setkey, setkey_r,
and fcrypt functions, while keeping fully binary compatibility
with existing (third-party) applications possibly still using
those funtions.  If such an application attemps to call one of
these functions, the corresponding function will indicate that
it is not supported by the system in a POSIX-compliant way.

For security reasons, the encrypt and encrypt_r functions will
also overwrite their data-block argument with random bits.

All existing binary executables linked against glibc's libcrypt
should work unmodified with the provided version of the
libcrypt.so.1 library in place.
EOF
%endif

%if %{with staticlib}
cat << EOF >> README.static
Applications that use certain legacy APIs supplied by glibc’s
libcrypt (encrypt, encrypt_r, setkey, setkey_r, and fcrypt)
cannot be compiled nor linked against the supplied build of
the object files provided in the static library libcrypt.a.
EOF
%endif


%build

mkdir -p %{_vpath_builddir}


# Build the default system library.
pushd %{_vpath_builddir}

CFLAGS="${CFLAGS:-%optflags}" ; export CFLAGS ; \
CXXFLAGS="${CXXFLAGS:-%optflags}" ; export CXXFLAGS ; \
FFLAGS="${FFLAGS:-%optflags -I%_fmoddir}" ; export FFLAGS ; \

%{configure} \
 %{common_configure_options}                    \
 --enable-hashes=%{hash_methods}                \
 --enable-obsolete-api=%{obsolete_api}          \
%if %{with libxcrypt_new_api}
 --enable-obsolete-api-enosys=%{obsolete_api}
%else
 --enable-obsolete-api-enosys=%{enosys_stubs}
%endif
%make_build
popd

%if %{with libxcrypt_compat_pkg}
mkdir -p %{_vpath_builddir}-compat

# Build the compatibility library.
pushd %{_vpath_builddir}-compat
%{configure} \
  %{common_configure_options}                    \
  --enable-hashes=%{compat_methods}              \
  --enable-obsolete-api=%{compat_api}            \
  --enable-obsolete-api-enosys=%{enosys_stubs}
%make_build
popd
%endif

mkdir -p %{_vpath_builddir}-all_possible_tests

# The configure scripts want to use -Wl,--wrap to run some
# special tests, which is not compatible with LTO.
%global system_lto_cflags_bak %{_lto_cflags}
%define _lto_cflags %{nil}

# Reset compiler flags in env.
unset CFLAGS
unset CXXFLAGS
unset FFLAGS
unset FCFLAGS
unset LDFLAGS
unset LT_SYS_LIBRARY_PATH

# Build a library suitable for all possible tests.
pushd %{_vpath_builddir}-all_possible_tests
%{configure} \
%if %{with libxcrypt_compat_pkg}
  %{common_configure_options}                    \
  --enable-hashes=all                            \
  --enable-obsolete-api=%{compat_api}            \
  --enable-obsolete-api-enosys=%{enosys_stubs}
%else
  %{common_configure_options}                    \
  --enable-hashes=%{hash_methods}                \
  --enable-obsolete-api=%{obsolete_api}          \
%if %{with libxcrypt_new_api}
  --enable-obsolete-api-enosys=%{obsolete_api}
%else
  --enable-obsolete-api-enosys=%{enosys_stubs}
%endif
%endif
%define _lto_cflags %{system_lto_cflags_bak}
%make_build
popd


%install
%if %{with libxcrypt_compat_pkg}
# Install the compatibility library.
%__make install -C %{_vpath_builddir}-compat DESTDIR=%{?buildroot} INSTALL="%{__install} -p"

# Cleanup everything we do not need from the compatibility library.
find %{buildroot} -type f -not -name 'libcrypt.so.%{csoc}*' -delete -print
find %{buildroot} -type l -not -name 'libcrypt.so.%{csoc}*' -delete -print
%endif

# Install the default system library.
%__make install -C %{_vpath_builddir} DESTDIR=%{?buildroot} INSTALL="%{__install} -p"

# Get rid of libtool crap.
find %{buildroot} -name '*.la' -delete -print

# Install documentation to shared %%{_docdir}/%{name}.
install -Dpm 0644 -t %{buildroot}%{_docdir}/%{name} \
  ChangeLog NEWS README* THANKS TODO

# Drop README.md as it is identical to README.
rm -f %{buildroot}%{_docdir}/%{name}/README.md


%check
build_dirs="%{_vpath_builddir}"
%if %{with libxcrypt_compat_pkg}
build_dirs="${build_dirs} %{_vpath_builddir}-compat"
%endif
build_dirs="${build_dirs} %{_vpath_builddir}-all_possible_tests"
for dir in ${build_dirs}; do
  %make_build -C ${dir} check || \
    {
      rc=$?;
      echo "-----BEGIN TESTLOG: ${dir}-----";
      cat ${dir}/test-suite.log;
      echo "-----END TESTLOG: ${dir}-----";
      exit $rc;
    }
done


%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig
%if %{with libxcrypt_compat_pkg}
%post compat -p /sbin/ldconfig
%postun compat -p /sbin/ldconfig
%endif


%files
%license AUTHORS COPYING.LIB LICENSING
%doc %dir %{_docdir}/%{name}
%doc %{_docdir}/%{name}/NEWS
%doc %{_docdir}/%{name}/README
%if %{with libxcrypt_new_api}
%doc %{_docdir}/%{name}/README%{distname}
%endif
%if %{with libxcrypt_enosys_stubs} && %{without libxcrypt_compat_pkg}
%doc %{_docdir}/%{name}/README.posix
%endif
%doc %{_docdir}/%{name}/THANKS
%{_libdir}/libcrypt.so.%{soc}
%{_libdir}/libcrypt.so.%{sov}
%{_mandir}/man5/crypt.5*


%if %{with libxcrypt_compat_pkg}
%files          compat
%if %{with libxcrypt_enosys_stubs}
%doc %{_docdir}/%{name}/README.posix
%endif
%{_libdir}/libcrypt.so.%{csoc}
%{_libdir}/libcrypt.so.%{csov}
%endif

%files          devel
%doc %{_docdir}/%{name}/ChangeLog
%doc %{_docdir}/%{name}/TODO
%{_libdir}/libcrypt.so
%if %{without libxcrypt_new_api}
%{_libdir}/libxcrypt.so
%endif
%{_includedir}/crypt.h
%if %{without libxcrypt_new_api}
%{_includedir}/xcrypt.h
%endif
%{_libdir}/pkgconfig/libcrypt.pc
%{_libdir}/pkgconfig/%{name}.pc
%{_mandir}/man3/crypt.3*
%{_mandir}/man3/crypt_r.3*
%{_mandir}/man3/crypt_ra.3*
%{_mandir}/man3/crypt_rn.3*
%{_mandir}/man3/crypt_checksalt.3*
%{_mandir}/man3/crypt_gensalt.3*
%{_mandir}/man3/crypt_gensalt_ra.3*
%{_mandir}/man3/crypt_gensalt_rn.3*
%{_mandir}/man3/crypt_preferred_method.3*


%if %{with staticlib}
%files          static
%dir %{_fipsdir}
%doc %{_docdir}/%{name}/README.static
%{_fipsdir}/libcrypt.a.hmac
%if %{without libxcrypt_new_api}
%{_fipsdir}/libxcrypt.a.hmac
%endif
%{_libdir}/libcrypt.a
%if %{without libxcrypt_new_api}
%{_libdir}/libxcrypt.a
%endif
%endif
