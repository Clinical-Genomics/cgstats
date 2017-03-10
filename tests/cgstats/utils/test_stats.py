from cgstats.utils import stats

def test_parse():
    assert stats.parse('tests/fixtures/150114_D00134_0168_AHB07NADXX/Unaligned/Basecall_Stats_HB07NADXX/Demultiplex_Stats.htm') == {
        'basemask': 'Y101,I6n,Y101',
        'rundate': u'150114',
        'support': {
            'idstring': 'bcl2fastq-1.8.4',
            'program': '/usr/local/bin/configureBclToFastq.pl',
            'command': {
                '--output-dir': 'DEMUX/150114_D00134_0168_AHB07NADXX/Unaligned',
                '--fastq-cluster-count': '0',
                '--sample-sheet': 'tests/fixtures/150114_D00134_0168_AHB07NADXX/Data/Intensities/BaseCalls/SampleSheet.csv',
                '--input-dir': 'tests/fixtures/150114_D00134_0168_AHB07NADXX/Data/Intensities/BaseCalls',
                '--use-bases-mask': 'Y101,I6n,Y101'
            },
            'system': {
                'OS': 'linux',
                'PID': '47668',
                'PERL_VERSION': 'v5.10.1',
                'PERL_EXECUTABLE': '/usr/bin/perl'
            }
        },
        'flowcell_pos': u'A',
        'machine': u'D00134',
        'flowcell': 'HB07NADXX',
    }
