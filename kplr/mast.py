#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (division, print_function, absolute_import,
                        unicode_literals)

__all__ = []

import requests


class API(object):

    base_url = "http://archive.stsci.edu/kepler/{0}/search.php"

    def request(self, category, **params):
        """
        Submit a request to the API and return the JSON response.

        :param category:
            The table that you want to search.

        :param params:
            Any other search parameters.

        """
        params["action"] = params.get("action", "Search")
        params["outputformat"] = "JSON"
        params["coordformat"] = "dec"
        params["verb"] = 3
        r = requests.get(self.base_url.format(category), params=params)
        if r.status_code != requests.codes.ok:
            r.raise_for_status()

        try:
            return r.json()
        except ValueError:
            return None

    def kois(self, **params):
        """
        Get a list of all the KOIs.

        """
        params["max_records"] = params.pop("max_records", 100)
        params["ordercolumn1"] = "kepoi"

        # # Special case to deal with the ``kepoi<N`` type queries.
        # if unicode(params.get("kepoi", " ")[0]) == "<":
        #     maxkoi = float(params["kepoi"][1:])
        # else:
        #     maxkoi = 1e10

        # Submit the initial request.
        kois = self.request("koi", **params)
        if kois is None:
            raise StopIteration()

        # Yield each KOI as a generator.
        for k in kois:
            yield KOI(k)

        raise StopIteration()

        # Try to get more KOIs if they exist.
        while True:
            params["kepoi"] = ">{0}".format(kois[-1]["kepoi"])
            kois = self.request("koi", **params)
            if kois is None:
                raise StopIteration()

            # Yield these ones too.
            for k in kois:
                if float(k["kepoi"]) > maxkoi:
                    raise StopIteration()
                yield KOI(k)

    def planets(self, **params):
        """
        Get a list of all the confirmed planets.

        """
        planets = self.request("confirmed_planets", **params)

        if planets is None:
            raise StopIteration()

        for p in planets:
            yield Planet(p)

    def data(self, kepler_id):
        """
        Get the :class:`bart.kepler.DataList` of observations associated with
        a particular Kepler ID.

        :param kepler_id:
            The Kepler ID.

        """
        data_list = self.request("data_search", ktc_kepler_id=kepler_id)
        if data_list is None:
            return []
        return APIDataList(data_list)


class APIModel(object):

    _id = "{_id}"
    _parameters = {"_id": None}

    def __init__(self, params):
        self._values = {}
        for k, v in self._parameters.iteritems():
            try:
                self._values[v[0]] = v[1](params.pop(k))
            except ValueError:
                self._values[v[0]] = None
        self._name = self._id.format(**self._values)

        if len(params):
            raise TypeError("Unrecognized parameters: {0}"
                            .format(", ".join(params.keys())))

    def __str__(self):
        return "<{0}({1})>".format(self.__class__.__name__, self._name)

    def __unicode__(self):
        return self.__str__()

    def __repr__(self):
        return self.__str__()

    def __getitem__(self, k):
        return self._values[k]

    def __getattr__(self, k):
        try:
            return self._values[k]
        except KeyError:
            raise AttributeError("{0} has no attribute '{1}'"
                                 .format(self.__class__.__name__, k))


class KOI(APIModel):

    _id = "{kepoi}"
    _parameters = {
        "Kepler ID": ("kepid", int),
        "KOI Name": ("kepoi_name", unicode),
        "KOI Number": ("kepoi", unicode),
        "Kepler Disposition": ("koi_pdisposition", unicode),
        "NExScI Disposition": ("koi_disposition", unicode),
        "RA (J2000)": ("degree_ra", float),
        "Dec (J2000)": ("degree_dec", float),
        "Time of Transit Epoch": ("koi_time0bk", float),
        "Time err1": ("koi_time0bk_err1", float),
        "Time_err2": ("koi_time0bk_err2", float),
        "Period": ("koi_period", float),
        "Period err1": ("koi_period_err1", float),
        "Period err2": ("koi_period_err2", float),
        "Transit Depth": ("koi_depth", float),
        "Depth err1": ("koi_depth_err1", float),
        "Depth err2": ("koi_depth_err2", float),
        "Duration": ("koi_duration", float),
        "Duration err1": ("koi_duration_err1", float),
        "Duration err2": ("koi_duration_err2", float),
        "Ingress Duration": ("koi_ingress", float),
        "Ingress err1": ("koi_ingress_err1", float),
        "Ingress err2": ("koi_ingress_err2", float),
        "Impact Parameter": ("koi_impact", float),
        "Impact Parameter err1": ("koi_impact_err1", float),
        "Impact Parameter err2": ("koi_impact_err2", float),
        "Inclination": ("koi_incl", float),
        "Inclination err1": ("koi_incl_err1", float),
        "Inclination err2": ("koi_incl_err2", float),
        "Semi-major Axis": ("koi_sma", float),
        "Semi-major Axus err1": ("koi_sma_err1", float),
        "Semi-major Axis err2": ("koi_sma_err2", float),
        "Eccentricity": ("koi_eccen", float),
        "Eccentricity err1": ("koi_eccen_err1", float),
        "Eccentricity err2": ("koi_eccen_err2", float),
        "Long of Periastron": ("koi_longp", float),
        "Long err1": ("koi_longp_err1", float),
        "Long err2": ("koi_longp_err2", float),
        "r/R": ("koi_ror", float),
        "r/R err1": ("koi_ror_err1", float),
        "r/R err2": ("koi_ror_err2", float),
        "a/R": ("koi_dor", float),
        "a/R err1": ("koi_dor_err1", float),
        "a/R err2": ("koi_dor_err2", float),
        "Planet Radius": ("koi_prad", float),
        "Planet Radius err1": ("koi_prad_err1", float),
        "Planet Radius err2": ("koi_prad_err2", float),
        "Teq": ("koi_teq", int),
        "Teq err1": ("koi_teq_err1", int),
        "Teq err2": ("koi_teq_err2", int),
        "Teff": ("koi_steff", int),
        "Teff err1": ("koi_steff_err1", int),
        "Teff err2": ("koi_steff_err2", int),
        "log(g)": ("koi_slogg", float),
        "log(g) err1": ("koi_slogg_err1", float),
        "log(g) err2": ("koi_slogg_err2", float),
        "Metallicity": ("koi_smet", float),
        "Metallicity err1": ("koi_smet_err1", float),
        "Metallicity err2": ("koi_smet_err2", float),
        "Stellar Radius": ("koi_srad", float),
        "Stellar Radius err1": ("koi_srad_err1", float),
        "Stellar Radius err2": ("koi_srad_err2", float),
        "Stellar Mass": ("koi_smass", float),
        "Stellar Mass err2": ("koi_smass_err2", float),
        "Stellar Mass err1": ("koi_smass_err1", float),
        "Age": ("koi_sage", float),
        "Age err1": ("koi_sage_err1", float),
        "Age err2": ("koi_sage_err2", float),
        "Provenance": ("koi_sparprov", unicode),
        "Quarters": ("koi_quarters", unicode),
        "Limb Darkening Model": ("koi_limbdark_mod", unicode),
        "Limb Darkening Coeff1": ("koi_ldm_coeff1", float),
        "Limb Darkening Coeff2": ("koi_ldm_coeff2", float),
        "Limb Darkening Coeff3": ("koi_ldm_coeff3", float),
        "Limb Darkening Coeff4": ("koi_ldm_coeff4", float),
        "Transit Number": ("koi_num_transits", int),
        "Max single event sigma": ("koi_max_sngle_ev", float),
        "Max Multievent sigma": ("koi_max_mult_ev", float),
        "KOI count": ("koi_count", int),
        "Binary Discrimination": ("koi_bin_oedp_sig", float),
        "False Positive Bkgnd ID": ("koi_fp_bkgid", unicode),
        "J-band diff": ("koi_fp_djmag", unicode),
        "Comments": ("koi_comment", unicode),
        "Transit Model": ("koi_trans_mod", unicode),
        "Transit Model SNR": ("koi_model_snr", float),
        "Transit Model DOF": ("koi_model_dof", float),
        "Transit Model chisq": ("koi_model_chisq", float),
        "FWM motion signif.": ("koi_fwm_stat_sig", float),
        "gmag": ("koi_gmag", float),
        "gmag err": ("koi_gmag_err", float),
        "rmag": ("koi_rmag", float),
        "rmag err": ("koi_rmag_err", float),
        "imag": ("koi_imag", float),
        "imag err": ("koi_imag_err", float),
        "zmag": ("koi_zmag", float),
        "zmag err": ("koi_zmag_err", float),
        "Jmag": ("koi_jmag", float),
        "Jmag err": ("koi_jmag_err", float),
        "Hmag": ("koi_hmag", float),
        "Hmag err": ("koi_hmag_err", float),
        "Kmag": ("koi_kmag", float),
        "Kmag err": ("koi_kmag_err", float),
        "kepmag": ("koi_kepmag", float),
        "kepmag err": ("koi_kepmag_err", float),
        "Delivery Name": ("koi_delivname", unicode),
        "FWM SRA": ("koi_fwm_sra", float),
        "FWM SRA err": ("koi_fwm_sra_err", float),
        "FWM SDec": ("koi_fwm_sdec", float),
        "FWM SDec err": ("koi_fwm_sdec_err", float),
        "FWM SRAO": ("koi_fwm_srao", float),
        "FWM SRAO err": ("koi_fwm_srao_err", float),
        "FWM SDeco": ("koi_fwm_sdeco", float),
        "FWM SDeco err": ("koi_fwm_sdeco_err", float),
        "FWM PRAO": ("koi_fwm_prao", float),
        "FWM PRAO err": ("koi_fwm_prao_err", float),
        "FWM PDeco": ("koi_fwm_pdeco", float),
        "FWM PDeco err": ("koi_fwm_pdeco_err", float),
        "Dicco MRA": ("koi_dicco_mra", float),
        "Dicco MRA err": ("koi_dicco_mra_err", float),
        "Dicco MDec": ("koi_dicco_mdec", float),
        "Dicco MDec err": ("koi_dicco_mdec_err", float),
        "Dicco MSky": ("koi_dicco_msky", float),
        "Dicco MSky err": ("koi_dicco_msky_err", float),
        "Dicco FRA": ("koi_dicco_fra", float),
        "Dicco FRA err": ("koi_dicco_fra_err", float),
        "Dicco FDec": ("koi_dicco_fdec", float),
        "Dicco FDec err": ("koi_dicco_fdec_err", float),
        "Dicco FSky": ("koi_dicco_fsky", float),
        "Dicco FSky err": ("koi_dicco_fsky_err", float),
        "Dikco MRA": ("koi_dikco_mra", float),
        "Dikco MRA err": ("koi_dikco_mra_err", float),
        "Dikco MDec": ("koi_dikco_mdec", float),
        "Dikco MDec err": ("koi_dikco_mdec_err", float),
        "Dikco MSky": ("koi_dikco_msky", float),
        "Dikco MSky err": ("koi_dikco_msky_err", float),
        "Dikco FRA": ("koi_dikco_fra", float),
        "Dikco FRA err": ("koi_dikco_fra_err", float),
        "Dikco FDec": ("koi_dikco_fdec", float),
        "Dikco FDec err": ("koi_dikco_fdec_err", float),
        "Dikco FSky": ("koi_dikco_fsky", float),
        "Dikco FSky err": ("koi_dikco_fsky_err", float),
        "Last Update": ("rowupdate", unicode),
    }


class Planet(APIModel):

    _id = "\"{kepler_name}\""
    _parameters = {
        "Planet Name": ("kepler_name", unicode),
        "Kepler ID": ("kepid", int),
        "KOI Name": ("kepoi_name", unicode),
        "Alt Name": ("alt_name", unicode),
        "KOI Number": ("koi", unicode),
        "RA (J2000)": ("degree_ra", float),
        "RA Error": ("ra_err", float),
        "Dec (J2000)": ("degree_dec", float),
        "Dec Error": ("dec_err", float),
        "2mass Name": ("tm_designation", unicode),
        "Planet temp": ("koi_teq", int),
        "Planet Radius": ("koi_prad", float),
        "Transit duration": ("koi_duration", float),
        "Period": ("koi_period", float),
        "Period err1": ("koi_period_err1", float),
        "Ingress Duration": ("koi_ingress", float),
        "Impact Parameter": ("koi_impact", float),
        "Inclination": ("koi_incl", float),
        "Provenance": ("koi_sparprov", unicode),
        "a/R": ("koi_dor", float),
        "Transit Number": ("koi_num_transits", int),
        "Transit Model": ("koi_trans_mod", unicode),
        "Time of transit": ("koi_time0bk", float),
        "Time of transit err1": ("koi_time0bk_err1", float),
        "Transit Depth": ("koi_depth", float),
        "Semi-major Axis": ("koi_sma", float),
        "r/R": ("koi_ror", float),
        "r/R err1": ("koi_ror_err1", float),
        "Age": ("koi_sage", float),
        "Metallicity": ("koi_smet", float),
        "Stellar Mass": ("koi_smass", float),
        "Stellar Radius": ("koi_srad", float),
        "Stellar Teff": ("koi_steff", int),
        "Logg": ("koi_slogg", float),
        "KEP Mag": ("koi_kepmag", float),
        "g Mag": ("koi_gmag", float),
        "r Mag": ("koi_rmag", float),
        "i Mag": ("koi_imag", float),
        "z Mag": ("koi_zmag", float),
        "J Mag": ("koi_jmag", float),
        "H Mag": ("koi_hmag", float),
        "K Mag": ("koi_kmag", float),
        "KOI List": ("koi_list_flag", unicode),
        "Last Update": ("koi_vet_date", unicode),
    }