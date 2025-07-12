#
# Conditional build:
%bcond_without	tests	# unit tests

Summary:	Core functionality for Pydantic validation and serialization
Summary(pl.UTF-8):	Podstawowa funkcjonalność walidacji i serializacji Pydantic
Name:		python3-pydantic_core
Version:	2.35.2
Release:	1
License:	MIT
Group:		Libraries/Python
#Source0Download: https://pypi.org/simple/pydantic-core/
Source0:	https://files.pythonhosted.org/packages/source/p/pydantic_core/pydantic_core-%{version}.tar.gz
# Source0-md5:	d4342593aad9b593c112da7ab0805ec1
# cargo vendor-filterer --platform='*-unknown-linux-*' --tier=2
# tar cJf pydantic_core-%{version}-vendor.tar.xz vendor Cargo.lock
Source1:	pydantic_core-%{version}-vendor.tar.xz
# Source1-md5:	054ff7422636ae4f206592c8f153e8e4
URL:		https://pypi.org/project/pydantic_core/
BuildRequires:	python3-build
BuildRequires:	python3-devel >= 1:3.9
BuildRequires:	python3-installer
BuildRequires:	python3-maturin >= 1
BuildRequires:	python3-maturin < 2
BuildRequires:	rust >= 1.75
%if %{with tests}
BuildRequires:	python3-dateutil
BuildRequires:	python3-dirty_equals
%if "%{_ver_lt %{py3_ver} 3.11}" == "1"
BuildRequires:	python3-exceptiongroup
%endif
BuildRequires:	python3-hypothesis
BuildRequires:	python3-inline_snapshot
# optional
#BuildRequires:	python3-numpy
#BuildRequires:	python3-pandas
BuildRequires:	python3-pytest
# optional
#BuildRequires:	python3-pytest-examples
BuildRequires:	python3-pytest-mock
BuildRequires:	python3-pytest-pretty
BuildRequires:	python3-pytest-run-parallel
BuildRequires:	python3-pytest-speed
BuildRequires:	python3-pytest-run-parallel
BuildRequires:	python3-pytest-timeout
BuildRequires:	python3-typing_extensions >= 4.13.0
BuildRequires:	python3-typing_inspection >= 0.4.1
BuildRequires:	python3-tzdata
%endif
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 2.044
BuildRequires:	tar >= 1:1.22
BuildRequires:	xz
Requires:	python3-modules >= 1:3.9
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
This package provides the core functionality for pydantic
(<https://docs.pydantic.dev/>) validation and serialization.

Pydantic-core is currently around 17x faster than pydantic V1.

%description -l pl.UTF-8
Ten pakiet dostarcza bazową funkcjonalność dla modułu pydantic
(<https://docs.pydantic.dev/>) służącego do kontroli poprawności i
serializacji klas.

Jest około 17x szybszy od pydantica V1.

%prep
%setup -q -n pydantic_core-%{version} -a1

# use our offline registry
export CARGO_HOME="$(pwd)/.cargo"

mkdir -p "$CARGO_HOME"
cat >.cargo/config.toml <<EOF
[source.crates-io]
replace-with = "vendored-sources"

[source.vendored-sources]
directory = "$PWD/vendor"
EOF

%build
export CARGO_BUILD_JOBS="%{__jobs}"
export CARGO_HOME="$(pwd)/.cargo"
export CARGO_OFFLINE=true
export RUSTFLAGS="%{rpmrustflags}"
export CARGO_TERM_VERBOSE=true
%ifarch x32
export CARGO_BUILD_TARGET=x86_64-unknown-linux-gnux32
export PKG_CONFIG_ALLOW_CROSS=1
export PYO3_CROSS_LIB_DIR=%{_libdir}
%endif

%py3_build_pyproject

%if %{with tests}
%{__python3} -m zipfile -e build-3/*.whl build-3-test
# test_leak_model hangs for me
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
PYTEST_PLUGINS=pytest_mock.plugin,pytest_run_parallel.plugin,pytest_speed,pytest_timeout \
PYTHONPATH=$(pwd)/build-3-test \
%{__python3} -m pytest tests -k 'not test_leak_model'
%endif

%install
rm -rf $RPM_BUILD_ROOT

export CARGO_HOME="$(pwd)/.cargo"
export CARGO_OFFLINE=true
export RUSTFLAGS="%{rpmrustflags}"
export CARGO_TERM_VERBOSE=true
%ifarch x32
export CARGO_BUILD_TARGET=x86_64-unknown-linux-gnux32
export PKG_CONFIG_ALLOW_CROSS=1
%endif

%py3_install_pyproject

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc LICENSE README.md
%dir %{py3_sitedir}/pydantic_core
%attr(755,root,root) %{py3_sitedir}/pydantic_core/_pydantic_core.cpython-*.so
%{py3_sitedir}/pydantic_core/_pydantic_core.pyi
%{py3_sitedir}/pydantic_core/py.typed
%{py3_sitedir}/pydantic_core/*.py
%{py3_sitedir}/pydantic_core/__pycache__
%{py3_sitedir}/pydantic_core-%{version}.dist-info
