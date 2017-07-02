require File.join(File.dirname(__FILE__), '..', 'spec_helper.rb');

describe "The Housing Insights tool", :type => :feature, :js => true do

  describe "in the Map View" do

    # Selenium navigates away from the page after each spec, so you need to
    # put 'visit' calls before each spec, not before all.
    before(:each) do
      visit '/'
    end

    describe "on load" do

      it "loads a Mapbox map" do
        expect(find('body')).to have_selector('.mapboxgl-canvas-container.mapboxgl-interactive')
      end

      it "displays a lefthand sidebar" do
        expect(find('body')).to have_selector('#sidebar-left')
      end

      it "displays a righthand sidebar" do
        expect(find('body')).to have_selector('#sidebar-right')  
      end

      it "displays a 'Subsidized Affordable Buildings' legend" do
        expect(find('body')).to have_selector('#category-legend')
        expect(find('#category-legend')).to have_content("Subsidized Affordable Buildings")
      end

    end

    describe "the left sidebar" do
      before(:each) do
        find('#sidebar-left')
      end

      describe "when the user first clicks the 'filters' tab" do
        before(:each) do
          find('#button-filters').click
        end

        it "displays the filters menu" do
          expect(find('#sidebar-left')).to have_selector('#filters.active')
        end

        it "doesn't display the layers menu" do
          expect(find('#sidebar-left')).to have_no_selector('#layers.active')
        end

        it "displays at least one filter title box" do
          expect(find('#sidebar-left')).to have_selector('.title.filter-title');
        end

        it "doesn't display sidebar content for a filter option" do
          expect(find('#sidebar-left')).to have_no_selector('#filter-components div.content.active')
        end

        describe "and clicks any title bar" do

          before(:each) do
            first('div .title.filter-title').click
          end

          it "displays sidebar content for a filter option" do
            expect(find('#sidebar-left')).to have_selector('div .filter.content.active')
          end

        end

        describe "and clicks a title bar for 'ward' (as a stand-in for any categorical filter)" do
          before(:each) do
            find('#filter-ward').click
          end

          it "shows a Semantic UI dropdown box" do
            expect(find('#filter-components')).to have_selector('div .ui.fluid.search.dropdown.dropdown-ward.selection.multiple.transition.visible')
          end

        end

      end

    end

  end

end