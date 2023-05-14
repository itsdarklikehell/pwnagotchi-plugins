package gps

import (
	"fmt"
	"time"
	"strconv"
	"github.com/bettercap/bettercap/session"
	"github.com/stratoberry/go-gpsd"
)

type GPS struct {
	session.SessionModule

	gpsdHost   string
	gpsdPort   int
	gps	   *gpsd.Session
}

func NewGPS(s *session.Session) *GPS {
	mod := &GPS{
		SessionModule: session.NewSessionModule("gps", s),
		gpsdHost:      "localhost",
		gpsdPort:      2947,
	}

	mod.AddParam(session.NewStringParameter("gps.gpsdHost",
		mod.gpsdHost,
		"",
		"Port GPSD is listening on (default: 2947)."))

	mod.AddParam(session.NewIntParameter("gps.gpsdPort",
		fmt.Sprintf("%d", mod.gpsdPort),
		"Host running GPSD (default: localhost)."))

	mod.AddHandler(session.NewModuleHandler("gps on", "",
		"Start acquiring from the GPS daemon.",
		func(args []string) error {
			return mod.Start()
		}))

	mod.AddHandler(session.NewModuleHandler("gps off", "",
		"Stop acquiring from the GPS daemon.",
		func(args []string) error {
			return mod.Stop()
		}))

	mod.AddHandler(session.NewModuleHandler("gps.show", "",
		"Show the last coordinates returned by the GPS daemon.",
		func(args []string) error {
			return mod.Show()
		}))

	return mod
}

func (mod *GPS) Name() string {
	return "gps"
}

func (mod *GPS) Description() string {
	return "A module for talking with the GPS daemon (GPSD) on a local or remote network interface."
}

func (mod *GPS) Author() string {
	return "Forrest"
}

func (mod *GPS) Configure() (err error) {
	if mod.Running() {
		return session.ErrAlreadyStarted(mod.Name())
	} else if err, mod.gpsdHost = mod.StringParam("gps.gpsdHost"); err != nil {
		return err
	} else if err, mod.gpsdPort = mod.IntParam("gps.gpsdPort"); err != nil {
		return err
	}

	mod.gps, err = gpsd.Dial(fmt.Sprintf("%s:%d", mod.gpsdHost, mod.gpsdPort))
	return
}

func (mod *GPS) Show() error {
	fmt.Printf("latitude:%f longitude:%f quality:%s satellites:%d altitude:%f\n",
		mod.Session.GPS.Latitude,
		mod.Session.GPS.Longitude,
		mod.Session.GPS.FixQuality,
		mod.Session.GPS.NumSatellites,
		mod.Session.GPS.Altitude)

	mod.Session.Refresh()

	return nil
}

func (mod *GPS) Start() error {
	if err := mod.Configure(); err != nil {
		return err
	}

	return mod.SetRunning(true, func() {

		mod.gps.AddFilter("TPV", func(r interface{}) {
			m := r.(*gpsd.TPVReport)
			mod.Session.GPS.Updated = time.Now()
			mod.Session.GPS.Latitude = m.Lat
			mod.Session.GPS.Longitude = m.Lon
			mod.Session.GPS.Altitude = m.Alt
			mod.Session.GPS.FixQuality = strconv.Itoa(int(m.Mode))
			//mod.Session.GPS.Separation = m.Separation
		})

		mod.gps.AddFilter("GST", func(r interface{}) {
			m := r.(*gpsd.GSTReport)
			mod.Session.GPS.Updated = time.Now()
			mod.Session.GPS.Latitude = m.Lat
			mod.Session.GPS.Longitude = m.Lon
			mod.Session.GPS.Altitude = m.Alt
		})

		mod.gps.AddFilter("SKY", func(r interface{}) {
			m := r.(*gpsd.SKYReport)
			mod.Session.GPS.Updated = time.Now()
			mod.Session.GPS.NumSatellites = int64(len(m.Satellites))
			mod.Session.GPS.HDOP = m.Hdop
		})

		mod.Info("started on %s:%d ...", mod.gpsdHost, mod.gpsdPort)
		for mod.Running() {
			done := mod.gps.Watch()
			<-done
		}

	})
}

func (mod *GPS) Stop() error {
	return mod.SetRunning(false, func() {
	})
}
